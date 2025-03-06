import requests
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_jwt_auth():
    # 1. Login to get a token
    login_data = {
        "username": "admin", 
        "password": "adminpassword"
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
            "Authorization": f"Bearer {token}"
        }
        
        # Test chat endpoint
        chat_response = requests.post(
            f"{BASE_URL}/chat/",
            headers=headers,
            json={"message": "What are the symptoms of diabetes?"}
        )
        
        print(f"Chat endpoint status: {chat_response.status_code}")
        print(f"Chat response: {chat_response.json() if chat_response.status_code == 200 else chat_response.text}")
        
        # Test images endpoint
        image_response = requests.get(
            f"{BASE_URL}/img/image/1",
            headers=headers
        )
        
        print(f"Image endpoint status: {image_response.status_code}")
        print(f"Image response: {image_response.json() if image_response.status_code == 200 else image_response.text}")
        
        # Test quiz endpoint (should work without authentication)
        quiz_response = requests.get(f"{BASE_URL}/quiz/generate/1")
        print(f"Quiz endpoint status: {quiz_response.status_code}")
        print(f"Quiz response: {quiz_response.json() if quiz_response.status_code == 200 else quiz_response.text}")
        
    else:
        print(f"Login failed: {response.text}")

if __name__ == "__main__":
    test_jwt_auth() 