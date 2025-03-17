from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
import logging
import os
from datetime import datetime
from ..services.image_service import ImageService
from config import Config
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Analyze a medical image without saving to database."""
    try:
        logger.info(f"Processing image analysis request: {file.filename}")
        logger.info(f"File content type: {file.content_type}")
        
        # Check if file exists
        if not file:
            logger.error("No file received")
            raise HTTPException(status_code=400, detail="No file received")
            
        # Check if file type is allowed
        if not ImageService.allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Invalid file type.")
            
        # Save file temporarily and analyze
        temp_file_path = os.path.join(Config.LOCAL_STORAGE_PATH, f"temp_{file.filename}")
        with open(temp_file_path, "wb") as buffer:
            file.file.seek(0)  # Ensure we're at the start of the file
            buffer.write(file.file.read())
        
        # Generate diagnosis
        description = ImageService.analyze_image(temp_file_path)
        
        # Get file size
        file_size = os.path.getsize(temp_file_path)
        
        # Remove temp file - no need to store it
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        logger.info(f"Image analyzed successfully: {file.filename}")
        
        # Format response according to requested structure
        return {
            "file_info": {
                "description": description,
                "filename": file.filename,
                "size": file_size,
                "upload_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "success": True,
            "message": "Image analyzed successfully"
        }
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/save")
async def save_image(file: UploadFile = File(...)):
    """Upload a medical image, generate a diagnosis, and save to database."""
    try:
        logger.info(f"Processing image upload to save: {file.filename}")
        
        # Check if file exists
        if not file:
            logger.error("No file received")
            raise HTTPException(status_code=400, detail="No file received")
            
        # Save file and generate diagnosis
        result = ImageService.save_uploaded_file(file)
        
        if not result:
            logger.error(f"Invalid file or file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Invalid file or file type.")
        
        logger.info(f"File uploaded successfully: {result['filename']}")
        return {
            "message": "File uploaded and saved successfully",
            "id": result["id"],
            "filename": result["filename"],
            "url": result["url_path"],
            "diagnosis": result["description"]
        }
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/random")
async def get_random_image():
    """Get a random image from the database."""
    try:
        image = ImageService.get_random_image()
        
        if not image:
            raise HTTPException(status_code=404, detail="No images found in database.")
        
        return image
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving random image: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the image.")

@router.get("/image/{image_id}")
async def get_image(image_id: int):
    """Get information about a specific image."""
    try:
        image = ImageService.get_image_by_id(image_id)
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found.")
        
        return image
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving image: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the image.")

@router.post("/regenerate/{image_id}")
async def regenerate_description(image_id: int):
    """Regenerate the description for an existing image."""
    try:
        result = ImageService.regenerate_description(image_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Image not found.")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating description: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while regenerating the description.")

# Simple test endpoint to verify the service is running
@router.get("/status")
async def status():
    """Check if the image service is running."""
    return {"status": "online", "service": "image analysis"} 