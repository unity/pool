from fastapi import APIRouter

from app.api.v1.endpoints import users, letta, rag

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(letta.router, prefix="/letta", tags=["letta"]) 
api_router.include_router(rag.router, prefix="/rag", tags=["rag"]) 
