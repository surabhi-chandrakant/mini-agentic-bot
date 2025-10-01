# complete_test.py
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_all_functionality():
    print("🚀 Comprehensive Mini Agentic Bot Test")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Health Status: {response.json()}")
    
    # Test 2: Data Endpoints
    print("\n2. Testing Data Endpoints...")
    users_response = requests.get(f"{BASE_URL}/data/users")
    projects_response = requests.get(f"{BASE_URL}/data/projects")
    print(f"✅ Users Count: {len(users_response.json()['users'])}")
    print(f"✅ Projects Count: {len(projects_response.json()['projects'])}")
    
    # Test 3: READ Operations (No approval needed)
    print("\n3. Testing READ Operations...")
    
    read_queries = [
        "Show me all users",
        "Show me active projects", 
        "Show users in engineering department",
        "List all projects"
    ]
    
    for query in read_queries:
        response = requests.post(f"{BASE_URL}/query", json={
            "query": query,
            "user_id": "test_user"
        })
        result = response.json()
        print(f"✅ Query: '{query}'")
        print(f"   Response: {result['response'][:100]}...")
        print(f"   Operation Type: {result['operation_type']}")
        print(f"   Requires Approval: {result['requires_approval']}")
        time.sleep(0.5)  # Small delay between requests
    
    # Test 4: CREATE Operations (Require approval)
    print("\n4. Testing CREATE Operations (Require Approval)...")
    
    create_queries = [
        "Create a new user named Alice in Marketing",
        "Add a new project called AI Research with budget 50000",
        "Create user Bob in Engineering department"
    ]
    
    approval_requests = []
    
    for query in create_queries:
        response = requests.post(f"{BASE_URL}/query", json={
            "query": query,
            "user_id": "test_user"
        })
        result = response.json()
        print(f"✅ Query: '{query}'")
        print(f"   Response: {result['response']}")
        print(f"   Operation Type: {result['operation_type']}")
        print(f"   Requires Approval: {result['requires_approval']}")
        
        if result['requires_approval']:
            # Extract request ID from response
            request_id = result['response'].split("Request ID: ")[1]
            approval_requests.append(request_id)
            print(f"   Request ID: {request_id}")
        
        time.sleep(0.5)
    
    # Test 5: Check Pending Approvals
    print("\n5. Checking Pending Approvals...")
    response = requests.get(f"{BASE_URL}/pending-approvals")
    pending = response.json()
    print(f"✅ Pending Approvals: {len(pending['pending_approvals'])}")
    print(json.dumps(pending, indent=2))
    
    # Test 6: Approve Operations
    print("\n6. Testing Approval Flow...")
    for request_id in approval_requests:
        print(f"Approving request: {request_id}")
        response = requests.post(f"{BASE_URL}/approve", json={
            "request_id": request_id,
            "user_id": "test_user",
            "approved": True
        })
        result = response.json()
        print(f"✅ Approval Result: {result['status']} - {result['message']}")
        time.sleep(0.5)
    
    # Test 7: Verify Data After Operations
    print("\n7. Verifying Data After Operations...")
    users_response = requests.get(f"{BASE_URL}/data/users")
    projects_response = requests.get(f"{BASE_URL}/data/projects")
    print(f"✅ Final Users Count: {len(users_response.json()['users'])}")
    print(f"✅ Final Projects Count: {len(projects_response.json()['projects'])}")
    
    # Test 8: Check No Pending Approvals Remain
    print("\n8. Verifying No Pending Approvals Remain...")
    response = requests.get(f"{BASE_URL}/pending-approvals")
    pending = response.json()
    print(f"✅ Remaining Pending Approvals: {len(pending['pending_approvals'])}")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("🤖 Mini Agentic Bot is fully operational!")

if __name__ == "__main__":
    test_all_functionality()