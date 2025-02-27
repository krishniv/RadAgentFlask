from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging
import shutil
import os
from ..services.image_service import ImageService
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload a medical image and generate a description."""
    try:
        logger.info(f"Received upload request for file: {file.filename}")
        logger.info(f"File content type: {file.content_type}")
        logger.info(f"File size: {file.size}")
        
        # Check if file exists
        if not file:
            logger.error("No file received")
            raise HTTPException(status_code=400, detail="No file received")
            
        result = ImageService.save_uploaded_file(file)
        
        if not result:
            logger.error(f"Invalid file or file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Invalid file or file type.")
        
        logger.info(f"File uploaded successfully: {result['filename']}")
        return {
            "message": "File uploaded successfully",
            "file_info": result
        }
    
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred while uploading the image: {str(e)}")

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

# Simple test endpoint just to verify upload functionality
@router.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Simple test endpoint for file uploads."""
    return {"filename": file.filename, "content_type": file.content_type} 