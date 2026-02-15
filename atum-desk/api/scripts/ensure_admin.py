import os
import sys
import psycopg
import uuid
import datetime
from passlib.context import CryptContext

# Add parent directory to path to import app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# DB Config (Default to config.py defaults)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "atum_desk")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection():
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        sys.exit(1)

def hash_password(password):
    return pwd_context.hash(password)

def ensure_admin():
    conn = get_db_connection()
    cur = conn.cursor()

    print("--- Verifying Organization ---")
    # Check Org
    cur.execute("SELECT id, name FROM organizations WHERE name = 'ATUM'")
    org = cur.fetchone()
    
    org_id = None
    if not org:
        print("Organization 'ATUM' not found. Creating...")
        cur.execute(
            "INSERT INTO organizations (name, domain, plan, settings) VALUES (%s, %s, %s, %s) RETURNING id",
            ('ATUM', 'atum.com', 'enterprise', '{"sla_enabled": true}')
        )
        org_id = cur.fetchone()[0]
        conn.commit()
        print(f"Created Org ID: {org_id}")
    else:
        org_id = org[0]
        print(f"Organization 'ATUM' exists. ID: {org_id}")

    print("\n--- Verifying Admin User ---")
    email = "admin@atum.io"
    password = "Admin@123"
    hashed = hash_password(password)

    cur.execute("SELECT id, email, role FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    now = datetime.datetime.now(datetime.timezone.utc)

    if not user:
        print(f"User '{email}' not found. Creating...")
        user_id = str(uuid.uuid4())
        
        # We populate ALL potentially required fields based on schema knowledge
        cur.execute(
            """
            INSERT INTO users (
                id, email, password_hash, full_name, role, organization_id, is_active,
                email_verified, is_email_verified, two_factor_enabled, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, 'ADMIN'::userrole, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id, email, hashed, 'System Admin', org_id, True,
                True, True, False, now, now
            )
        )
        conn.commit()
        print(f"Created Admin User: {email} (ID: {user_id})")
    else:
        print(f"User '{email}' exists. Updating password AND role to ensure access...")
        cur.execute(
            "UPDATE users SET password_hash = %s, organization_id = %s, role = 'ADMIN'::userrole, is_active = true, is_email_verified = true, email_verified = true WHERE email = %s",
            (hashed, org_id, email)
        )
        conn.commit()
        print("Password updated.")

    print("\n--- Verifying Data Tables ---")
    tables = ['tickets', 'comments', 'audit_log']
    for t in tables:
        try:
            cur.execute(f"SELECT count(*) FROM {t}")
            count = cur.fetchone()[0]
            print(f"Table '{t}': {count} rows")
        except Exception as e:
            print(f"Error checking table {t}: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    ensure_admin()
