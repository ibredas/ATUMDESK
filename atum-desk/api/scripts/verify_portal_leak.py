import asyncio
import httpx
import uuid
import sys

# Configuration
API_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin_test@atum.io"
ADMIN_UPASS = "password123"

async def run_test():
    async with httpx.AsyncClient(base_url=API_URL, timeout=10.0) as client:
        print("🔒 Starting Portal Leak Test...")

        # 1. Login Admin to create users
        res = await client.post("/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_UPASS})
        if res.status_code != 200:
            print(f"❌ Admin login failed: {res.text}")
            return
        admin_token = res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. Create Agent & Customer
        agent_email = f"agent_leak_{uuid.uuid4().hex[:6]}@atum.io"
        cust_email = f"cust_leak_{uuid.uuid4().hex[:6]}@atum.io"
        
        # Create Agent
        await client.post("/users", json={
            "email": agent_email, "full_name": "Agent Leak", "password": "password123", "role": "agent"
        }, headers=admin_headers)
        
        # Create Customer
        await client.post("/users", json={
            "email": cust_email, "full_name": "Customer Leak", "password": "password123", "role": "customer_user"
        }, headers=admin_headers)

        # 3. Login as Agent & Customer
        # Agent
        res = await client.post("/auth/login", data={"username": agent_email, "password": "password123"})
        agent_token = res.json()["access_token"]
        agent_headers = {"Authorization": f"Bearer {agent_token}"}
        
        # Customer
        res = await client.post("/auth/login", data={"username": cust_email, "password": "password123"})
        cust_token = res.json()["access_token"]
        cust_headers = {"Authorization": f"Bearer {cust_token}"}
        print("✅ setup: Users created and logged in.")

        # 4. Agent creates INTERNAL Article
        print("\n[TEST 1] Internal Article Leakage")
        internal_title = f"Internal Secret {uuid.uuid4().hex[:6]}"
        res = await client.post("/kb/articles", json={
            "title": internal_title,
            "content": "Secret Content",
            "is_internal": True,
            "is_published": True # Published but Internal
        }, headers=agent_headers)
        if res.status_code != 200:
            print(f"❌ Failed to create internal article: {res.text}")
            return
        internal_id = res.json()["id"]
        print(f"   -> Agent created Internal Article: {internal_title} ({internal_id})")

        # 5. Customer tries to list (Search)
        res = await client.get("/kb/articles", params={"search": internal_title}, headers=cust_headers)
        items = res.json()
        found = any(i["id"] == internal_id for i in items)
        if found:
            print("❌ FAILURE: Customer Sqw Internal Article in List!")
        else:
            print("✅ SUCCESS: Internal Article NOT in Customer List.")

        # 6. Customer tries to GET ID
        res = await client.get(f"/kb/articles/{internal_id}", headers=cust_headers)
        if res.status_code == 404:
            print("✅ SUCCESS: Customer GET Internal ID returned 404.")
        else:
            print(f"❌ FAILURE: Customer GET Internal ID returned {res.status_code}!")
            
        # 7. Agent creates PUBLIC Article
        print("\n[TEST 2] Public Article Visibility")
        public_title = f"Public Info {uuid.uuid4().hex[:6]}"
        res = await client.post("/kb/articles", json={
            "title": public_title,
            "content": "Public Content",
            "is_internal": False,
            "is_published": True
        }, headers=agent_headers)
        public_id = res.json()["id"]
        print(f"   -> Agent created Public Article: {public_title}")

        # 8. Customer tries to list
        res = await client.get("/kb/articles", params={"search": public_title}, headers=cust_headers)
        items = res.json()
        found = any(i["id"] == public_id for i in items)
        if found:
            print("✅ SUCCESS: Customer Saw Public Article in List.")
        else:
            print("❌ FAILURE: Customer DID NOT see Public Article.")

if __name__ == "__main__":
    asyncio.run(run_test())
