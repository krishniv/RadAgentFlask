import requests
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_email_based_jwt_auth():
    """Test JWT authentication using email address"""
    # 1. Login using email instead of username
    print("=== TESTING EMAIL-BASED JWT AUTHENTICATION ===")
    
    # Get credentials from env or use defaults
    test_email = "admin@example.com"  # Should match create_admin.py
    test_password = "adminpassword"   # Should match create_admin.py
    
    print(f"Attempting to login with email: {test_email}")
    
    # Note: OAuth2 form requires "username" field even though we're sending an email
    login_data = {
        "username": test_email,  # Using email in username field
        "password": test_password
    }
    
    response = requests.post(
        f"{BASE_URL}/token", 
        data=login_data  # Form data, not JSON
    )
    
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"Received token: {token[:20]}...")
        
        # 2. Use the token to access protected endpoints
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test chat endpoint
        print("\nTesting protected chat endpoint...")
        chat_response = requests.post(
            f"{BASE_URL}/chat/",
            headers=headers,
            json={"message": "What are the symptoms of diabetes?"}
        )
        
        print(f"Chat endpoint status: {chat_response.status_code}")
        if chat_response.status_code == 200:
            print("Successfully accessed protected chat endpoint!")
            chat_data = chat_response.json()
            print(f"Chat response: {chat_data['response'][:100]}...")
        else:
            print(f"Failed to access chat endpoint: {chat_response.text}")
        
        # Test images endpoint
        print("\nTesting protected image endpoint...")
        image_response = requests.get(
            f"{BASE_URL}/img/image/1",
            headers=headers
        )
        
        print(f"Image endpoint status: {image_response.status_code}")
        # Status 404 is acceptable if image with ID 1 doesn't exist
        if image_response.status_code in [200, 404]:
            print("Successfully accessed protected image endpoint!")
        else:
            print(f"Failed to access image endpoint: {image_response.text}")
        
        # Test quiz endpoint (should work without authentication)
        print("\nTesting public quiz endpoint...")
        quiz_response = requests.get(f"{BASE_URL}/quiz/generate/1")
        print(f"Quiz endpoint status: {quiz_response.status_code}")
        
        if quiz_response.status_code == 200:
            print("Successfully accessed public quiz endpoint!")
        else:
            print(f"Failed to access quiz endpoint: {quiz_response.text}")
        
    else:
        print(f"Login failed: {response.text}")

    print("\n=== EMAIL-BASED JWT AUTH TEST COMPLETE ===")

if __name__ == "__main__":
    test_email_based_jwt_auth() 