"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import auth, chat, admin

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="KIT CampusAI - AI-powered knowledge base and secure chat platform",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print(f"✅ {settings.APP_NAME} started successfully")
    print(f"📚 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_db()
    print(f"👋 {settings.APP_NAME} shutting down")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}/auth", tags=["Authentication"])
app.include_router(chat.router, prefix=f"/api/{settings.API_VERSION}/chat", tags=["Chat"])
app.include_router(admin.router, prefix=f"/api/{settings.API_VERSION}/admin", tags=["Admin"])


@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc):
    """Handle ValueError exceptions"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
