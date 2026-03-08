import json
import requests
from typing import Dict

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.schemas import AREAS

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def normalize_percentages(data: Dict[str, float]) -> Dict[str, float]:
    """
    Asegura:
    - todas las áreas existen
    - valores entre 0 y 100
    - suma cercana a 100
    """
    clean = {}

    for area in AREAS:
        value = data.get(area, 0)
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0

        if value < 0:
            value = 0.0
        if value > 100:
            value = 100.0

        clean[area] = value

    total = sum(clean.values())

    if total <= 0:
        # fallback uniforme si algo sale mal
        uniform = round(100 / len(AREAS), 2)
        clean = {area: uniform for area in AREAS}
        diff = round(100 - sum(clean.values()), 2)
        first_key = AREAS[0]
        clean[first_key] += diff
        return clean

    normalized = {}
    for area, value in clean.items():
        normalized[area] = round((value / total) * 100, 2)

    # ajustar diferencia por redondeo
    diff = round(100 - sum(normalized.values()), 2)
    first_key = AREAS[0]
    normalized[first_key] = round(normalized[first_key] + diff, 2)

    return normalized


def classify_text_with_ai(user_text: str) -> Dict[str, float]:
    system_prompt = f"""
Eres un clasificador de reportes ciudadanos.

Tu tarea es analizar el texto del usuario y repartir porcentajes de relación
entre estas áreas EXACTAMENTE con estos nombres:

{json.dumps(AREAS, ensure_ascii=False)}

Reglas:
1. Responde SOLO en JSON válido.
2. Debes devolver un objeto con una única clave: "percentages".
3. Dentro de "percentages" deben aparecer TODAS las áreas EXACTAMENTE.
4. Los valores deben ser números.
5. La suma de todos los porcentajes debe dar aproximadamente 100.
6. Usa el significado semántico del texto, aunque el usuario escriba informal.
7. Si el texto tiene relación con varias áreas, distribuye los porcentajes.
8. No agregues explicaciones, solo JSON.
"""

    user_prompt = f'Texto del usuario: "{user_text}"'

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "area_classification",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "percentages": {
                            "type": "object",
                            "properties": {
                                "Baches": {"type": "number"},
                                "Agua": {"type": "number"},
                                "Alumbrado": {"type": "number"},
                                "Semaforos": {"type": "number"},
                                "Transporte Publico": {"type": "number"},
                                "Poda urbano": {"type": "number"},
                                "Inundaciones": {"type": "number"},
                                "Recolección de basura": {"type": "number"}
                            },
                            "required": [
                                "Baches",
                                "Agua",
                                "Alumbrado",
                                "Semaforos",
                                "Transporte Publico",
                                "Poda urbano",
                                "Inundaciones",
                                "Recolección de basura"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "required": ["percentages"],
                    "additionalProperties": False
                }
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Clasificador de Areas Ciudadanas"
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    data = response.json()

    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)

    percentages = parsed.get("percentages", {})
    return normalize_percentages(percentages)