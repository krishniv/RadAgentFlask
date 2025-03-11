import os

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Database configuration
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///medical_agent.db')
    
    # Authentication settings
    ENABLE_AUTH = os.environ.get('ENABLE_AUTH', 'False').lower() == 'true'
    
    # Storage configuration
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'local')  # 'local', 's3', 'azure', etc.
    
    # Local storage settings
    LOCAL_STORAGE_PATH = os.environ.get('LOCAL_STORAGE_PATH', './storage/medical_images')
    
    # URL base for accessing images
    IMAGES_URL_BASE = os.environ.get('IMAGES_URL_BASE', '/images/')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'} 
    
    # Hugging Face settings
    HF_TOKEN = os.environ.get('HF_TOKEN', '')
    HF_MODEL_ID = os.environ.get('HF_MODEL_ID', 'mistralai/Mistral-7B-Instruct-v0.2')
    HF_IMAGE_MODEL_ID = os.environ.get('HF_IMAGE_MODEL_ID', 'microsoft/BiomedVLP-CXR-BERT-specialized') 