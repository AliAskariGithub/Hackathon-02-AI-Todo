"""
Test script to check all tables in Neon database
"""
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse

load_dotenv()

# Get the database URL from environment
db_url = os.getenv('DATABASE_URL')

if 'neon.tech' in db_url:
    # Parse the URL manually to extract components
    parsed = urlparse(db_url)

    # Connect directly without using SQLAlchemy
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip('/'),
        user=parsed.username,
        password=parsed.password,
        sslmode='require'  # This is needed for Neon
    )

    cursor = conn.cursor()

    # Check all tables in the public schema
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)

    all_tables = [row[0] for row in cursor.fetchall()]
    print(f"All tables in public schema: {all_tables}")

    # Check the users table specifically (might be plural)
    cursor.execute("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables
           WHERE table_schema = 'public'
           AND table_name = 'users'
        );
    """)

    users_exists = cursor.fetchone()[0]
    print(f"Users table exists: {users_exists}")

    # Check if 'user' table exists (without s)
    cursor.execute("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables
           WHERE table_schema = 'public'
           AND table_name = 'user'
        );
    """)

    user_exists = cursor.fetchone()[0]
    print(f"User table exists: {user_exists}")

    cursor.close()
    conn.close()