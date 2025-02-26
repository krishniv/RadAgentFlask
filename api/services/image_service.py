import os
import uuid
from werkzeug.utils import secure_filename
from config import Config
from database import db_session, MedicalImage
from ..modelcaption import generate_medical_description

class ImageService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_uploaded_file(file):
        """Save an uploaded file and return its metadata"""
        if not file or not ImageService.allowed_file(file.filename):
            return None
            
        # Generate a secure filename with UUID to avoid conflicts
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        # Create directory if it doesn't exist
        if not os.path.exists(Config.LOCAL_STORAGE_PATH):
            os.makedirs(Config.LOCAL_STORAGE_PATH, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(Config.LOCAL_STORAGE_PATH, unique_filename)
        file.save(file_path)
        
        # Generate description
        description = generate_medical_description(file_path)
        
        # Create database record
        url_path = f"{Config.IMAGES_URL_BASE}{unique_filename}"
        medical_image = MedicalImage(
            filename=unique_filename,
            filepath=file_path,
            url_path=url_path,
            description=description
        )
        
        db_session.add(medical_image)
        db_session.commit()
        
        return {
            "id": medical_image.id,
            "filename": unique_filename,
            "url_path": url_path,
            "description": description
        }
    
    @staticmethod
    def get_random_image():
        """Get a random image from the database"""
        # This could use SQLAlchemy's random() function or similar
        # For SQLite, we can use ORDER BY RANDOM() LIMIT 1
        image = db_session.query(MedicalImage).order_by('RANDOM()').first()
        
        if not image:
            return None
            
        return {
            "id": image.id,
            "filename": image.filename,
            "url_path": image.url_path,
            "description": image.description
        }
    
    @staticmethod
    def get_image_by_id(image_id):
        """Get an image by its ID"""
        image = db_session.query(MedicalImage).filter_by(id=image_id).first()
        
        if not image:
            return None
            
        return {
            "id": image.id,
            "filename": image.filename,
            "url_path": image.url_path,
            "description": image.description
        } 