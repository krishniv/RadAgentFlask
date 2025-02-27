from fastapi import APIRouter, HTTPException
import logging
from ..services.quiz_service import QuizService
import traceback

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
        
        # Check if we got empty data
        if not quiz_data:
            logger.warning("No quiz questions could be generated. Check if database has images.")
            return {"questions": [], "warning": "No questions could be generated."}
            
        return {"questions": quiz_data}
    
    except Exception as e:
        # Log full traceback for debugging
        logger.error(f"Error generating options: {e}")
        logger.error(traceback.format_exc())
        
        # Return a clear JSON error response
        return {"error": f"An error occurred: {str(e)}"} 