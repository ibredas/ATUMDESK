import os
import sys
import psycopg

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# DB Config (Default to config.py defaults)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "atum_desk")

def check_db():
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        cur = conn.cursor()
        
        print("--- Users ---")
        cur.execute("SELECT email, role, organization_id, is_active, is_email_verified FROM users")
        for row in cur.fetchall():
            print(f"User: {row}")
            
        print("\n--- Organizations ---")
        cur.execute("SELECT id, name, domain FROM organizations")
        for row in cur.fetchall():
            print(f"Org: {row}")
            
        print("\n--- Ticket Org Distribution ---")
        cur.execute("SELECT organization_id, COUNT(*) FROM tickets GROUP BY organization_id")
        for row in cur.fetchall():
            print(f"Org {row[0]}: {row[1]} tickets")

        print("\n--- Table Counts ---")
        for table in ['tickets', 'audit_log', 'job_queue']:
            try:
                cur.execute(f"SELECT count(*) FROM {table}")
                print(f"{table}: {cur.fetchone()[0]}")
            except Exception as e:
                print(f"{table}: Error {e}")
                conn.rollback()

        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    check_db()
