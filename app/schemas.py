from pydantic import BaseModel
from typing import List

AREAS = [
    "Baches",
    "Agua",
    "Alumbrado",
    "Semaforos",
    "Transporte Publico",
    "Poda urbano",
    "Inundaciones",
    "Recolección de basura",
]


class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    text: str
    predicted_area: str
    confidence: float


class ConfirmRequest(BaseModel):
    predicted_area: str
    is_correct: bool


class SelectAreaRequest(BaseModel):
    area: str