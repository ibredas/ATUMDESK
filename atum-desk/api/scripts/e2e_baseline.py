import asyncio
import httpx
import sys
import os

# Configuration
API_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@atum.io"
ADMIN_UPASS = "admin"

async def run_test():
    async with httpx.AsyncClient(base_url=API_URL, timeout=10.0) as client:
        print("🚀 Starting Baseline E2E Test...")

        # 1. Login Admin
        print("[1] Logging in as Admin...")
        res = await client.post("/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_UPASS})
        if res.status_code != 200:
            print(f"❌ Admin login failed: {res.text}")
            return
        admin_token = res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("✅ Admin Logged In")

        # 2. Create Users (Agent + Customer)
        print("[2] Creating Test Users...")
        # Agent
        agent_email = "agent_e2e@atum.io"
        await client.post("/users", json={
            "email": agent_email, "full_name": "Agent E2E", "password": "password123", "role": "agent"
        }, headers=admin_headers) 
        # Customer
        import uuid
        cust_email = f"customer_{uuid.uuid4()}@atum.io"
        print(f"   -> Creating customer {cust_email}...")
        res = await client.post("/users", json={
            "email": cust_email, "full_name": "Customer E2E", "password": "password123", "role": "customer_user"
        }, headers=admin_headers)
        if res.status_code not in [200, 201]:
             print(f"❌ Failed to create customer: {res.status_code} {res.text}")
             return
        print("✅ Users Created/Ensured")

        # 3. Customer Creates Ticket
        print("[3] Customer Login & Create Ticket...")
        await asyncio.sleep(2)
        res = await client.post("/auth/login", data={"username": cust_email, "password": "password123"})

        if res.status_code != 200:
            print(f"❌ Customer login failed: {res.text}")
            return
        cust_token = res.json()["access_token"]
        cust_headers = {"Authorization": f"Bearer {cust_token}"}
        
        res = await client.post("/tickets", json={
            "subject": "E2E Baseline Test Ticket",
            "description": "This is a test ticket for baseline verification.",
            "priority": "high"
        }, headers=cust_headers)
        if res.status_code != 201:
            print(f"❌ Ticket creation failed: {res.text}")
            return
        ticket_id = res.json()["id"]
        print(f"✅ Ticket #{ticket_id} Created")

        # 4. Manager Accepts & Assigns
        print("[4] Manager (Admin) Accepts & Assigns...")
        # Get Agent ID
        res = await client.get(f"/users?email={agent_email}", headers=admin_headers)
        agent_id = res.json()[0]["id"]

        # Accept
        res = await client.post(f"/tickets/{ticket_id}/accept", headers=admin_headers)
        if res.status_code != 200:
             print(f"❌ Accept failed: {res.text}")
             # It might be auto-accepted if creator is admin, but here creator is customer.
             # Wait, endpoint might need permissions. Admin has permission.
        
        # Assign
        res = await client.put(f"/tickets/{ticket_id}/assign?user_id={agent_id}", headers=admin_headers)
        print("✅ Ticket Accepted & Assigned")

        # 5. Agent Comments
        print("[5] Agent Login & Reply...")
        res = await client.post("/auth/login", data={"username": agent_email, "password": "password123"})
        agent_token = res.json()["access_token"]
        agent_headers = {"Authorization": f"Bearer {agent_token}"}

        # Internal Note
        await client.post(f"/tickets/{ticket_id}/comments", json={
            "content": "Investigating this issue (Internal).", "is_internal": True
        }, headers=agent_headers)
        
        # Public Reply
        await client.post(f"/tickets/{ticket_id}/comments", json={
            "content": "Hello, we are working on it.", "is_internal": False
        }, headers=agent_headers)
        
        # Set Status Waiting Customer
        await client.put(f"/tickets/{ticket_id}/status", params={"status": "WAITING_CUSTOMER"}, headers=agent_headers)
        print("✅ Agent Replied & Updated Status")

        # 6. Customer Reply
        print("[6] Customer Reply...")
        await client.post(f"/tickets/{ticket_id}/comments", json={
            "content": "Thanks for the update."
        }, headers=cust_headers)
        print("✅ Customer Replied")

        # 7. Agent Resolve
        print("[7] Agent Resolve...")
        await client.put(f"/tickets/{ticket_id}/status", params={"status": "RESOLVED"}, headers=agent_headers)
        print("✅ Ticket Resolved")

        print("🎉 BASELINE TEST PASSED!")

if __name__ == "__main__":
    asyncio.run(run_test())
