"""
Dell Boca Boys - Customer Portal API

FastAPI application serving the customer portal backend.
Provides REST API endpoints for customer authentication, workflow management,
analytics, and real-time notifications.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import routers
from .customer_routes import router as customer_router

# Create FastAPI app
app = FastAPI(
    title="Dell Boca Boys - Customer Portal API",
    description="Backend API for the Dell Boca Boys workflow automation customer portal",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware - configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",  # React dev server
        "http://localhost:5173",  # Vite default port
        # Add production frontend URL here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customer_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "dell-boca-boys-customer-api",
        "version": "2.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Dell Boca Boys - Customer Portal API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Disable in production
        log_level="info"
    )
