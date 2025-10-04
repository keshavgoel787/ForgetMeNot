import os, uuid, json, pandas as pd
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv()

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)
cursor = conn.cursor()
print("✅ Connected to Snowflake")

# Load metadata CSV
df = pd.read_csv("metadata.csv")

# Insert each clip into Snowflake (no embeddings yet)
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO MEMORY_VAULT (
            id, title, clip_name, description, scene_label, emotion_label, context_tags, clip_url
        )
        SELECT %s, %s, %s, %s, %s, %s, PARSE_JSON(%s), %s
    """, (
        str(uuid.uuid4()),
        row["title"],
        row["clip_name"],
        row["description"],
        row["scene_label"],
        row["emotion_label"],
        json.dumps(eval(row["context_tags"])),
        f"https://storage.example.com/{row['clip_name']}"
    ))


conn.commit()
print("✅ All clips inserted successfully (no embeddings).")

# Close connection
cursor.close()
conn.close()
