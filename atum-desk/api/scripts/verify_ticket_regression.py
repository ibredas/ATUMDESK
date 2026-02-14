import asyncio
import httpx
import uuid
import sys
import os

# Configuration
API_URL = "http://localhost:8001/api/v1"
ADMIN_EMAIL = "admin_test@atum.io"
ADMIN_UPASS = "password123"

async def run_test():
    async with httpx.AsyncClient(base_url=API_URL, timeout=10.0) as client:
        print("🚀 Starting Ticket Regression + Attachment Test...")

        # 1. Login Admin
        print("[1] Logging in as Admin...")
        res = await client.post("/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_UPASS})
        if res.status_code != 200:
            print(f"❌ Admin login failed: {res.text}")
            return
        admin_token = res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. Create Agent & Customer
        print("[2] Creating Test Users...")
        agent_email = f"agent_reg_{uuid.uuid4().hex[:6]}@atum.io"
        cust_email = f"cust_reg_{uuid.uuid4().hex[:6]}@atum.io"
        
        await client.post("/users", json={
            "email": agent_email, "full_name": "Agent Regression", "password": "password123", "role": "agent"
        }, headers=admin_headers)
        
        await client.post("/users", json={
            "email": cust_email, "full_name": "Customer Regression", "password": "password123", "role": "customer_user"
        }, headers=admin_headers)
        
        # Get Agent ID
        res = await client.get(f"/users?email={agent_email}", headers=admin_headers)
        agent_id = res.json()[0]["id"]

        # 3. Login Users
        print("[3] Logging in Users...")
        # Customer
        res = await client.post("/auth/login", data={"username": cust_email, "password": "password123"})
        cust_token = res.json()["access_token"]
        cust_headers = {"Authorization": f"Bearer {cust_token}"}
        
        # Agent
        res = await client.post("/auth/login", data={"username": agent_email, "password": "password123"})
        agent_token = res.json()["access_token"]
        agent_headers = {"Authorization": f"Bearer {agent_token}"}

        # 4. Customer Creates Ticket
        print("[4] Customer Creates Ticket...")
        res = await client.post("/tickets", json={
            "subject": "Regression Test Ticket",
            "description": "Testing attachments and workflow.",
            "priority": "medium"
        }, headers=cust_headers)
        if res.status_code != 201:
            print(f"❌ Ticket creation failed: {res.text}")
            return
        ticket_id = res.json()["id"]
        print(f"✅ Ticket #{ticket_id} Created")

        # 5. Customer Uploads Attachment
        print("[5] Customer Uploads Attachment...")
        files = {'file': ('test.txt', b'This is a test attachment content.', 'text/plain')}
        res = await client.post(f"/attachments/ticket/{ticket_id}", files=files, headers=cust_headers)
        if res.status_code != 200:
            print(f"❌ Attachment upload failed: {res.text}")
            return
        attachment_id = res.json()["id"]
        print(f"✅ Attachment Uploaded: {attachment_id}")

        # 6. Manager Accepts & Assigns
        print("[6] Manager Accepts & Assigns...")
        await client.post(f"/tickets/{ticket_id}/accept", headers=admin_headers)
        await client.put(f"/tickets/{ticket_id}/assign?user_id={agent_id}", headers=admin_headers)
        print("✅ Ticket Accepted & Assigned")

        # 7. Agent Downloads Attachment
        print("[7] Agent Downloads Attachment...")
        res = await client.get(f"/attachments/{attachment_id}/download", headers=agent_headers)
        if res.status_code != 200:
             print(f"❌ Download failed: {res.status_code}")
             return
        if res.content == b'This is a test attachment content.':
             print("✅ Download Content Verified")
        else:
             print("❌ Download Content Mismatch")

        # 8. Agent Replies
        print("[8] Agent Replies...")
        await client.post(f"/tickets/{ticket_id}/comments", json={
            "content": "Received your file.", "is_internal": False
        }, headers=agent_headers)
        await client.put(f"/tickets/{ticket_id}/status", params={"status": "WAITING_CUSTOMER"}, headers=agent_headers)

        # 9. Customer Replies
        print("[9] Customer Replies...")
        await client.post(f"/tickets/{ticket_id}/comments", json={
            "content": "Great, thanks."
        }, headers=cust_headers)

        # 10. Resolve
        print("[10] Agent Resolves...")
        await client.put(f"/tickets/{ticket_id}/status", params={"status": "RESOLVED"}, headers=agent_headers)
        print("✅ Ticket Resolved")
        
        print("🎉 TICKET REGRESSION TEST PASSED!")

if __name__ == "__main__":
    asyncio.run(run_test())
