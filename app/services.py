import json
from typing import Dict

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.schemas import AREAS

client = OpenAI(api_key=OPENAI_API_KEY)


def normalize_percentages(data: Dict[str, float]) -> Dict[str, float]:
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

    # Si el modelo devuelve todo mal
    if total <= 0:
        uniform = round(100 / len(AREAS), 2)
        clean = {area: uniform for area in AREAS}
        diff = round(100 - sum(clean.values()), 2)
        clean[AREAS[0]] += diff
        return clean

    normalized = {}

    for area, value in clean.items():
        normalized[area] = round((value / total) * 100, 2)

    diff = round(100 - sum(normalized.values()), 2)
    normalized[AREAS[0]] = round(normalized[AREAS[0]] + diff, 2)

    return normalized


def classify_text_with_ai(user_text: str) -> Dict[str, float]:

    system_prompt = f"""
Eres un clasificador de reportes ciudadanos.

Debes analizar el texto del usuario y repartir porcentajes de relación
entre estas áreas EXACTAMENTE con estos nombres:

{json.dumps(AREAS, ensure_ascii=False)}

Reglas:
- Responde SOLO JSON válido
- Debe existir una clave llamada "percentages"
- Deben aparecer TODAS las áreas
- Los valores deben ser números
- La suma aproximada debe ser 100
"""

    user_prompt = f'Texto del usuario: "{user_text}"'

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    # 🔹 limpiar markdown que a veces devuelve el modelo
    clean_content = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(clean_content)
    except Exception:
        raise ValueError(f"Respuesta no válida del modelo: {content}")

    percentages = parsed.get("percentages", {})

    return normalize_percentages(percentages)