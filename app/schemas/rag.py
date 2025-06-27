from pydantic import BaseModel

class RAGQuestion(BaseModel):
    question: str

class RAGAnswer(BaseModel):
    answer: str 