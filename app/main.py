from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    AnalyzeRequest,
    ConfirmRequest,
    SelectAreaRequest,
    AREAS
)

from app.services import classify_text_with_ai

app = FastAPI(title="Clasificador de Áreas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


# -----------------------------
# 1️⃣ Analizar texto
# -----------------------------
@app.post("/analyze")
def analyze(req: AnalyzeRequest):

    text = req.text.strip()

    percentages = classify_text_with_ai(text)

    top_area = max(percentages, key=percentages.get)
    top_percentage = percentages[top_area]

    return {
        "text": text,
        "predicted_area": top_area,
        "confidence": top_percentage
    }


# -----------------------------
# 2️⃣ Confirmar si el área es correcta
# -----------------------------
@app.post("/confirm-area")
def confirm_area(req: ConfirmRequest):

    if req.is_correct:

        return {
            "message": f"Bienvenido al área de {req.predicted_area}. Tu reporte será atendido."
        }

    return {
        "message": "Selecciona el área correcta",
        "areas": AREAS
    }


# -----------------------------
# 3️⃣ Usuario selecciona área manual
# -----------------------------
@app.post("/select-area")
def select_area(req: SelectAreaRequest):

    if req.area not in AREAS:
        raise HTTPException(status_code=400, detail="Área inválida")

    return {
        "message": f"Bienvenido al área de {req.area}. Tu reporte será atendido."
    }