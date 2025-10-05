import os, uuid, pandas as pd, json
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

def main():
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=ACCOUNT,
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    cur = conn.cursor()

    # Clear existing data to avoid duplicates
    print("🗑️  Clearing existing data from MEMORY_VAULT...")
    cur.execute("TRUNCATE TABLE MEMORY_VAULT")
    conn.commit()

    df = pd.read_csv("data/metadata.csv")
    print(f"📊 Uploading {len(df)} records to MEMORY_VAULT...")
    print("   Using Snowflake CORTEX.EMBED_TEXT_768 for embeddings...")

    success_count = 0
    skip_count = 0

    for idx, row in df.iterrows():
        desc = str(row["description"]).strip() if pd.notna(row["description"]) else ""
        summary = str(row.get("event_summary", "")).strip() if pd.notna(row.get("event_summary", "")) else ""
        file_type = str(row["file_type"]).strip() if pd.notna(row["file_type"]) else ""
        file_url = str(row["file_url"]).strip() if pd.notna(row["file_url"]) else ""

        # Remove surrounding quotes if present (from CSV parsing)
        if desc.startswith('"') and desc.endswith('"'):
            desc = desc[1:-1]
        if summary.startswith('"') and summary.endswith('"'):
            summary = summary[1:-1]

        # Generate embedding using description (prioritize description over summary)
        text_for_embedding = desc or summary

        if not text_for_embedding or text_for_embedding == "nan":
            print(f"  ⚠️  Skipping {row['file_name']} - no text content")
            skip_count += 1
            continue

        # Parse people JSON string to array
        people_json = row["people"] if pd.notna(row["people"]) else "[]"
        people_list = json.loads(people_json)
        people_sql = json.dumps(people_list)

        # Use Snowflake CORTEX function to generate embedding directly in SQL
        sql = """
            INSERT INTO MEMORY_VAULT
            (id, event_name, file_name, file_type, description, people, event_summary, file_url, embedding)
            SELECT %s,%s,%s,%s,%s,PARSE_JSON(%s)::ARRAY,%s,%s,
                   SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s)
        """

        try:
            cur.execute(sql, (
                str(uuid.uuid4()),
                row["event_name"] if pd.notna(row["event_name"]) else "",
                row["file_name"] if pd.notna(row["file_name"]) else "",
                file_type,
                desc,
                people_sql,
                summary,
                file_url,
                text_for_embedding
            ))
            success_count += 1
        except Exception as e:
            print(f"  ❌ Error uploading {row['file_name']}: {e}")
            skip_count += 1
            continue

        if (idx + 1) % 10 == 0:
            conn.commit()  # Commit every 10 records
            print(f"  ✓ Processed {idx + 1}/{len(df)} records ({success_count} uploaded, {skip_count} skipped)")

    conn.commit()
    print(f"✅ Upload complete: {success_count} records uploaded, {skip_count} skipped")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
