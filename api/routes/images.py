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

# Simple test endpoint to verify the service is running
@router.get("/status")
async def status():
    """Check if the image service is running."""
    return {"status": "online", "service": "image analysis"} 