"""Quick script to check registered routes."""
import sys
sys.path.insert(0, '.')

print("Importing main app...")
from src.main import app

print(f"\nApp has {len(app.routes)} routes:")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"  {route.path}")
    if hasattr(route, 'methods'):
        print(f"    Methods: {route.methods}")
