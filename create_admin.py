import os
from dotenv import load_dotenv
from database import db_session, User
from api.login import get_password_hash

# Load environment variables
load_dotenv()

def create_admin_user():
    """Create an admin user if it doesn't exist already"""
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "adminpassword")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    
    # Check if admin user already exists
    existing_admin = db_session.query(User).filter(User.username == admin_username).first()
    if existing_admin:
        print(f"Admin user '{admin_username}' already exists")
        return
    
    # Create the admin user
    hashed_password = get_password_hash(admin_password)
    admin_user = User(
        username=admin_username,
        email=admin_email,
        password_hash=hashed_password,
        is_active=True,
        is_admin=True
    )
    
    db_session.add(admin_user)
    db_session.commit()
    print(f"Admin user '{admin_username}' created successfully")

if __name__ == "__main__":
    create_admin_user() 