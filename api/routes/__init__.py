from fastapi import APIRouter

def get_routers():
    from .quiz import router as quiz_router
    from .images import router as images_router
    # Import other routers when implemented
    return [quiz_router, images_router] 