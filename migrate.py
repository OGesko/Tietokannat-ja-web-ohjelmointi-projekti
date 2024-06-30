import os
from datetime import datetime, timedelta
import random
import psycopg2
from dotenv import load_dotenv
from hash_pwd import hash_password

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

# Function to read and execute SQL from schema.sql
def migrate_database():
    try:
        # Connect to the database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        # Drop existing tables if they exist
        drop_tables_sql = '''
            DROP TABLE IF EXISTS "transaction_category";
            DROP TABLE IF EXISTS "transaction";
            DROP TABLE IF EXISTS "account";
            DROP TABLE IF EXISTS "user";
            DROP TABLE IF EXISTS "category";
        '''

        cursor.execute(drop_tables_sql)
        conn.commit()

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

def populate_database():
    try:
        # Connect to the database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        # Clear existing data
        clear_tables_sql = '''
            TRUNCATE TABLE "transaction" CASCADE;
            TRUNCATE TABLE "transaction_category" CASCADE;
            TRUNCATE TABLE "account" CASCADE;
            TRUNCATE TABLE "user" CASCADE;
            TRUNCATE TABLE "category" CASCADE;
        '''
        cursor.execute(clear_tables_sql)
        conn.commit()

        # Insert basic categories
        categories = [
            ('Groceries',),
            ('Utilities',),
            ('Transportation',),
            ('Entertainment',),
            ('Miscellaneous',)
        ]
        insert_category_sql = 'INSERT INTO "category" (name) VALUES (%s)'
        cursor.executemany(insert_category_sql, categories)
        conn.commit()

        # Insert admin user
        admin_password = hash_password("admin_password")
        admin_user_sql = '''
            INSERT INTO "user" (username, pwd, admin)
            VALUES (%s, %s, %s)
            RETURNING id
        '''
        cursor.execute(admin_user_sql, ("admin", admin_password, True))
        admin_user_id = cursor.fetchone()[0]
        conn.commit()

        # Insert example users with accounts and transactions
        users = [
            ('user1', 'password1'),
            ('user2', 'password2'),
            ('user3', 'password3'),
            ('user4', 'password4'),
            ('user5', 'password5')
        ]

        for username, password in users:
            pwd = hash_password(password)
            user_insert_sql = '''
                INSERT INTO "user" (username, pwd)
                VALUES (%s, %s)
                RETURNING id
            '''
            cursor.execute(user_insert_sql, (username, pwd))
            user_id = cursor.fetchone()[0]

            for i in range(2):  # Each user will have 2 accounts
                account_insert_sql = '''
                    INSERT INTO "account" (user_id, name, balance)
                    VALUES (%s, %s, %s)
                    RETURNING id
                '''
                account_name = f"{username}_account_{i+1}"
                cursor.execute(account_insert_sql, (user_id, account_name, 1000.00))  # Starting balance
                account_id = cursor.fetchone()[0]

                # Insert transactions for the last year
                start_date = datetime.now() - timedelta(days=365)
                end_date = datetime.now()
                delta = timedelta(days=30)  # Monthly transactions

                while start_date < end_date:
                    transaction_insert_sql = '''
                        INSERT INTO "transaction" (description, amount, timestamp, user_id, account_id)
                        VALUES (%s, %s, %s, %s, %s)
                    '''
                    amount = round(random.uniform(10, 200), 2)  # Random amount
                    transaction_data = (
                        f"{username} transaction {i+1}",
                        amount,
                        start_date,
                        user_id,
                        account_id
                    )
                    cursor.execute(transaction_insert_sql, transaction_data)
                    start_date += delta

                conn.commit()

        print("Database populated with initial data.")

    except psycopg2.Error as e:
        print(f"Error during data population: {e}")

    finally:
        # Close connections
        cursor.close()
        conn.close()

# Entry point
if __name__ == "__main__":
    migrate_database()
    populate_database()
