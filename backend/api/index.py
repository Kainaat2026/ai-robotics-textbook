"""Minimal Vercel test."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Minimal test working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test-import")
async def test_import():
    """Test importing the main app."""
    import sys
    import os

    results = {
        "cwd": os.getcwd(),
        "python_path": sys.path[:5],
        "files_in_cwd": [],
        "src_exists": False,
        "import_error": None
    }

    try:
        results["files_in_cwd"] = os.listdir(".")[:10]
    except Exception as e:
        results["files_in_cwd"] = str(e)

    try:
        results["src_exists"] = os.path.exists("src")
        if results["src_exists"]:
            results["src_contents"] = os.listdir("src")[:10]
    except Exception as e:
        results["src_exists"] = str(e)

    try:
        sys.path.insert(0, os.getcwd())
        from src.main import app as main_app
        results["import_success"] = True
        results["routes_count"] = len(main_app.routes)
    except Exception as e:
        import traceback
        results["import_error"] = str(e)
        results["import_traceback"] = traceback.format_exc()

    return results

handler = app
