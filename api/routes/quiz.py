from fastapi import APIRouter, HTTPException
import logging
from ..services.quiz_service import QuizService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
quiz_service = QuizService()

@router.get("/generate/{amount}")
async def generate_options(amount: int):
    """Generate quiz options for the requested amount of questions."""
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0.")
        
        quiz_data = quiz_service.generate_multiple_questions(amount)
        return {"questions": quiz_data}
    
    except Exception as e:
        logger.error(f"Error generating options: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating quiz options.") 