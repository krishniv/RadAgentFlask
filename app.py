from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from config import Config
from api.routes import quiz, images, chat, wallet

# Create FastAPI app
app = FastAPI(title="Medical Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files for serving images
os.makedirs(Config.LOCAL_STORAGE_PATH, exist_ok=True)
app.mount("/images", StaticFiles(directory=Config.LOCAL_STORAGE_PATH), name="images")

# Include routers
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["wallet"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Medical Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)