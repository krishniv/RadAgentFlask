from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import logging
from ..services.image_service import ImageService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload a medical image and generate a description."""
    try:
        result = ImageService.save_uploaded_file(file)
        
        if not result:
            raise HTTPException(status_code=400, detail="Invalid file or file type.")
        
        return {
            "message": "File uploaded successfully",
            "file_info": result
        }
    
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading the image.")

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