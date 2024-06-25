import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

# Function to read and execute SQL from schema.sql
def migrate_database():
    try:
        # Connect to the database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        # Path to your schema.sql file
        script_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

        # Read SQL statements from schema.sql
        with open(script_path, 'r') as f:
            sql_commands = f.read()

        # Execute the SQL commands
        cursor.execute(sql_commands)
        conn.commit()

        print("Migration completed successfully.")

    except psycopg2.Error as e:
        print(f"Error during migration: {e}")

    finally:
        # Close connections
        cursor.close()
        conn.close()

# Entry point
if __name__ == "__main__":
    migrate_database()
