"""Main FastAPI application for AI-Powered Textbook backend - v2."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database connection (commented out for demo - no DB needed)
# from src.db.connection import close_db

# Import routers
print("=== IMPORTING TRANSLATION ROUTER ===")
from src.routes import translation
print("=== TRANSLATION ROUTER IMPORTED ===")

print("=== IMPORTING CHATBOT ROUTER ===")
try:
    from src.routes import chatbot
    print(f"=== CHATBOT ROUTER IMPORTED SUCCESSFULLY ===")
except Exception as e:
    print(f"!!! CHATBOT ROUTER IMPORT FAILED: {type(e).__name__}: {e} !!!")
    import traceback
    traceback.print_exc()
    chatbot = None

print("=== IMPORTING PROGRESS ROUTER ===")
try:
    from src.routes import progress
    print(f"=== PROGRESS ROUTER IMPORTED SUCCESSFULLY ===")
except Exception as e:
    print(f"!!! PROGRESS ROUTER IMPORT FAILED: {type(e).__name__}: {e} !!!")
    import traceback
    traceback.print_exc()
    progress = None

print("=== IMPORTING QUIZ ROUTER ===")
try:
    from src.routes import quiz
    print(f"=== QUIZ ROUTER IMPORTED SUCCESSFULLY ===")
except Exception as e:
    print(f"!!! QUIZ ROUTER IMPORT FAILED: {type(e).__name__}: {e} !!!")
    import traceback
    traceback.print_exc()
    quiz = None

print("=== IMPORTING AUTH ROUTER ===")
try:
    from src.routes import auth
    print(f"=== AUTH ROUTER IMPORTED SUCCESSFULLY ===")
except Exception as e:
    print(f"!!! AUTH ROUTER IMPORT FAILED: {type(e).__name__}: {e} !!!")
    import traceback
    traceback.print_exc()
    auth = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Initialize database connections
        - Create Qdrant collection if needed
        - Load configuration

    Shutdown:
        - Close database connections
        - Cleanup resources
    """
    # Startup
    print("Starting up AI Textbook API...")
    # TODO: Initialize Qdrant collection
    # await vector_store.create_collection()

    yield

    # Shutdown
    print("Shutting down AI Textbook API...")
    # await close_db()  # Commented out for demo - no DB


# Create FastAPI application
app = FastAPI(
    title="AI-Powered Physical AI & Robotics Textbook API",
    description="Backend API for AI-enhanced interactive textbook with RAG chatbot, quizzes, and personalization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS - allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": "AI Textbook API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Service health status and metadata
    """
    return {
        "status": "healthy",
        "checks": {
            "api": "ok",
            # TODO: Add database and Qdrant health checks
            # "database": "ok" if await check_db() else "error",
            # "vector_store": "ok" if await check_qdrant() else "error",
        },
    }


# Include routers
print("=== REGISTERING CHATBOT ROUTER ===")
if chatbot is not None:
    try:
        app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])
        print(f"=== CHATBOT ROUTER REGISTERED ({len(chatbot.router.routes)} routes) ===")
    except Exception as e:
        print(f"!!! CHATBOT ROUTER REGISTRATION FAILED: {type(e).__name__}: {e} !!!")
        import traceback
        traceback.print_exc()
else:
    print("!!! CHATBOT ROUTER WAS NOT IMPORTED - SKIPPING !!!")

print("=== REGISTERING TRANSLATION ROUTER ===")
app.include_router(translation.router, prefix="/api", tags=["Translation"])
print(f"=== TRANSLATION ROUTER REGISTERED ({len(translation.router.routes)} routes) ===")

print("=== REGISTERING PROGRESS ROUTER ===")
if progress is not None:
    try:
        app.include_router(progress.router, prefix="/api", tags=["Progress"])
        print(f"=== PROGRESS ROUTER REGISTERED ({len(progress.router.routes)} routes) ===")
    except Exception as e:
        print(f"!!! PROGRESS ROUTER REGISTRATION FAILED: {type(e).__name__}: {e} !!!")
        import traceback
        traceback.print_exc()
else:
    print("!!! PROGRESS ROUTER WAS NOT IMPORTED - SKIPPING !!!")

print("=== REGISTERING QUIZ ROUTER ===")
if quiz is not None:
    try:
        app.include_router(quiz.router, prefix="/api", tags=["Quiz"])
        print(f"=== QUIZ ROUTER REGISTERED ({len(quiz.router.routes)} routes) ===")
    except Exception as e:
        print(f"!!! QUIZ ROUTER REGISTRATION FAILED: {type(e).__name__}: {e} !!!")
        import traceback
        traceback.print_exc()
else:
    print("!!! QUIZ ROUTER WAS NOT IMPORTED - SKIPPING !!!")

print("=== REGISTERING AUTH ROUTER ===")
if auth is not None:
    try:
        app.include_router(auth.router, prefix="/api", tags=["Auth"])
        print(f"=== AUTH ROUTER REGISTERED ({len(auth.router.routes)} routes) ===")
    except Exception as e:
        print(f"!!! AUTH ROUTER REGISTRATION FAILED: {type(e).__name__}: {e} !!!")
        import traceback
        traceback.print_exc()
else:
    print("!!! AUTH ROUTER WAS NOT IMPORTED - SKIPPING !!!")

print(f"=== TOTAL APP ROUTES: {len(app.routes)} ===")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "true").lower() == "true",
    )
