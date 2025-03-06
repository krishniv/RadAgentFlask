from fastapi import APIRouter

def get_routers():
    from .quiz import router as quiz_router
    from .images import router as images_router
    from .chat import router as chat_router
    from .auth import router as auth_router
    # Import other routers when implemented
    return [quiz_router, images_router, chat_router, auth_router] 