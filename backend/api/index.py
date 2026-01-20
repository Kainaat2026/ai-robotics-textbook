"""Vercel serverless entry point for FastAPI."""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app

# Vercel expects the app to be named 'app' or 'handler'
handler = app
