from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.api.v1.api import api_router
from app.services.rag_service import RAGService

# Initialize logging first
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

logger.info(f"Starting {settings.project_name} v{settings.version}")

# rag_service = RAGService()
# rag_service.index_rag()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://noli.com",
        "https://www.noli.com",
        "https://www.noli.com",
        "http://localhost:3000",
        "http://localhost:3001",  # Proxy server
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",  # Proxy server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

# Include API router
app.include_router(api_router, prefix=settings.api_v1_str)

logger.info(f"API router included with prefix: {settings.api_v1_str}")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to SmartBar!"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"} 
