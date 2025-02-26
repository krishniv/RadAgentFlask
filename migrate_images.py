import os
from database import db_session, MedicalImage
from config import Config
from api.modelcaption import generate_medical_description

def migrate_existing_images():
    """Migrate existing images to the database."""
    # Get list of image files
    image_files = [f for f in os.listdir(Config.LOCAL_STORAGE_PATH) 
                  if os.path.isfile(os.path.join(Config.LOCAL_STORAGE_PATH, f))
                  and f.split('.')[-1].lower() in Config.ALLOWED_EXTENSIONS]
    
    for filename in image_files:
        # Check if already in database
        existing = db_session.query(MedicalImage).filter_by(filename=filename).first()
        if existing:
            print(f"Image {filename} already in database, skipping.")
            continue
        
        file_path = os.path.join(Config.LOCAL_STORAGE_PATH, filename)
        url_path = f"{Config.IMAGES_URL_BASE}{filename}"
        
        # Generate description
        description = generate_medical_description(file_path)
        
        # Create database record
        medical_image = MedicalImage(
            filename=filename,
            filepath=file_path,
            url_path=url_path,
            description=description
        )
        
        db_session.add(medical_image)
        print(f"Added {filename} to database.")
    
    db_session.commit()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_existing_images() 