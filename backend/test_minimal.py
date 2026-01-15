"""Minimal test to see if chatbot router works."""
from fastapi import FastAPI
from src.routes import chatbot

app = FastAPI()

print(f"Chatbot router has {len(chatbot.router.routes)} routes")

app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])

print(f"App has {len(app.routes)} routes after including chatbot router:")
for route in app.routes:
    if hasattr(route, 'path') and '/api' in route.path:
        print(f"  {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
