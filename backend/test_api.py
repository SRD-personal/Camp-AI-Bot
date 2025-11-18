"""
Simple test to verify FastAPI can start without database
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import google.generativeai as genai
from app.core.config import settings

app = FastAPI(title="KIT CampusAI Test")

@app.get("/")
def root():
    return {"status": "running", "app": "KIT CampusAI"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test-gemini")
async def test_gemini():
    """Test Gemini API connection"""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Hello from KIT CampusAI!' in one sentence")
        return {
            "status": "success",
            "gemini_response": response.text,
            "message": "Gemini API is working!"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/test-config")
def test_config():
    """Test configuration"""
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "oauth_configured": bool(settings.GOOGLE_CLIENT_ID),
        "cors_origins": settings.CORS_ORIGINS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
