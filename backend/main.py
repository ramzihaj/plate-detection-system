from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.controllers import auth_controller, plate_controller, user_controller
from app.core.config import settings
from app.core.database import init_db
import uvicorn
import os

app = FastAPI(
    title="Plate Detection System API",
    description="Advanced license plate detection and recognition system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await init_db()
    print("✅ Database connected")
    print(f"✅ Server running on http://{settings.HOST}:{settings.PORT}")

# Include routers
app.include_router(auth_controller.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(plate_controller.router, prefix="/api/plates", tags=["Plate Detection"])
app.include_router(user_controller.router, prefix="/api/users", tags=["Users"])

# Serve uploaded images
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {
        "message": "Plate Detection System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False  # Disabled to avoid PyTorch multiprocessing issues on Windows
    )
