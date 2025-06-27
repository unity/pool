from fastapi import APIRouter, HTTPException
from app.services.rag_service import RAGService
from app.schemas.rag import RAGQuestion, RAGAnswer

router = APIRouter()
rag_service = RAGService()

@router.post("/ask", response_model=RAGAnswer)
def ask_rag(question: RAGQuestion):
    try:
        answer = rag_service.ask_agent(question.question, category=None)
        return RAGAnswer(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 