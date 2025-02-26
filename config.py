import os

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Database configuration
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///medical_agent.db')
    
    # Storage configuration
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'local')  # 'local', 's3', 'azure', etc.
    
    # Local storage settings
    LOCAL_STORAGE_PATH = os.environ.get('LOCAL_STORAGE_PATH', './storage/medical_images')
    
    # URL base for accessing images
    IMAGES_URL_BASE = os.environ.get('IMAGES_URL_BASE', '/images/')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'} 