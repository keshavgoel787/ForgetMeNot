"""
Create THERAPIST_EXPERIENCES table in Snowflake
Run this once to set up the therapist experiences feature
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scripts.lib.snowflake_client import SnowflakeClient


def create_therapist_experiences_table():
    """Create the THERAPIST_EXPERIENCES table"""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS THERAPIST_EXPERIENCES (
        id VARCHAR(36) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        general_context TEXT,
        experience_data VARIANT,
        total_memories INT,
        created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
        updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """

    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_therapist_experiences_title ON THERAPIST_EXPERIENCES(title)",
        "CREATE INDEX IF NOT EXISTS idx_therapist_experiences_created_at ON THERAPIST_EXPERIENCES(created_at)"
    ]

    try:
        with SnowflakeClient() as client:
            cursor = client.cursor

            # Create table
            print("📋 Creating THERAPIST_EXPERIENCES table...")
            cursor.execute(create_table_sql)
            print("✅ Table created successfully")

            # Create indexes
            print("\n📊 Creating indexes...")
            for idx_sql in create_indexes_sql:
                cursor.execute(idx_sql)
            print("✅ Indexes created successfully")

            # Verify
            print("\n🔍 Verifying table...")
            cursor.execute("SHOW TABLES LIKE 'THERAPIST_EXPERIENCES'")
            result = cursor.fetchone()

            if result:
                print(f"✅ Table verified: {result[1]}")

                # Show table structure
                cursor.execute("DESCRIBE TABLE THERAPIST_EXPERIENCES")
                columns = cursor.fetchall()

                print("\n📋 Table structure:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")

                print("\n✅ Setup complete! THERAPIST_EXPERIENCES table is ready.")
            else:
                print("❌ Table verification failed")

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise


if __name__ == "__main__":
    create_therapist_experiences_table()
