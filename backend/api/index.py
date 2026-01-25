"""Vercel serverless entry point for FastAPI."""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.main import app
    handler = app
except Exception as e:
    # If import fails, create a minimal app that shows the error
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import traceback

    error_app = FastAPI()
    error_message = f"{type(e).__name__}: {str(e)}"
    error_traceback = traceback.format_exc()

    @error_app.get("/{path:path}")
    async def catch_all(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": error_message,
                "traceback": error_traceback,
                "python_path": sys.path[:5],
                "cwd": os.getcwd(),
            }
        )

    app = error_app
    handler = error_app
