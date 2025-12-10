from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# -----------------------------
# Definición de ítems IPIP-100
# -----------------------------
# NOTA: Aquí van solo 10 ítems como ejemplo estructural.
# Luego simplemente seguimos agregando ítems hasta llegar a item100.

IPIP_ITEMS: List[Dict] = [
    {"id": "item1", "text": "Cumplo con mis compromisos a tiempo.", "factor": "CON"},
    {"id": "item2", "text": "Me siento tenso o nervioso con frecuencia.", "factor": "NEU"},
    {"id": "item3", "text": "Disfruto conocer gente nueva.", "factor": "EXT"},
    {"id": "item4", "text": "Me esfuerzo por ser amable con los demás.", "factor": "AGR"},
    {"id": "item5", "text": "Me interesa aprender cosas nuevas.", "factor": "OPE"},
    {"id": "item6", "text": "Pierdo la calma con facilidad.", "factor": "NEU"},
    {"id": "item7", "text": "Soy organizado en mi trabajo diario.", "factor": "CON"},
    {"id": "item8", "text": "Prefiero actividades tranquilas antes que eventos sociales grandes.", "factor": "EXT"},
    {"id": "item9", "text": "Confío en las buenas intenciones de las personas.", "factor": "AGR"},
    {"id": "item10", "text": "Disfruto explorar ideas poco comunes o creativas.", "factor": "OPE"},
    # Aquí continuamos hasta item100 con el mismo formato
]

# Etiquetas descriptivas de cada factor
FACTOR_LABELS = {
    "NEU": "Estabilidad Emocional (bajo Neuroticismo)",
    "CON": "Responsabilidad / Escrupulosidad",
    "OPE": "Apertura a la Experiencia",
    "AGR": "Amabilidad",
    "EXT": "Extraversión",
}

# -----------------------------
# Rutas principales
# -----------------------------

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/test", response_class=HTMLResponse)
async def show_test(request: Request):
    return templates.TemplateResponse(
        "test.html",
        {"request": request, "items": IPIP_ITEMS}
    )


@app.post("/test", response_class=HTMLResponse)
async def submit_test(request: Request, **form_data):
    
    # Extraer textos discursivos
    texto_funcional = form_data.pop("texto_funcional", "").strip()
    texto_situacional = form_data.pop("texto_situacional", "").strip()

    # Acumuladores por factor
    scores = {"NEU": 0, "CON": 0, "OPE": 0, "AGR": 0, "EXT": 0}
    counts = {"NEU": 0, "CON": 0, "OPE": 0, "AGR": 0, "EXT": 0}

    # Sumar puntajes IPIP
    for item in IPIP_ITEMS:
        item_id = item["id"]
        factor = item["factor"]
        if item_id in form_data:
            try:
                value = int(form_data[item_id])
            except ValueError:
                value = 0
            scores[factor] += value
            counts[factor] += 1

    # Calcular promedios
    avg_scores = {}
    for factor in scores.keys():
        if counts[factor] > 0:
            avg_scores[factor] = round(scores[factor] / counts[factor], 2)
        else:
            avg_scores[factor] = None

    # Placeholder análisis TRUNAJOD (integración futura)
    analisis_discursivo = {
        "comentario_general": "Integración con TRUNAJOD pendiente.",
        "texto_funcional_length": len(texto_funcional.split()),
        "texto_situacional_length": len(texto_situacional.split()),
    }

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "scores": scores,
            "avg_scores": avg_scores,
            "factor_labels": FACTOR_LABELS,
            "texto_funcional": texto_funcional,
            "texto_situacional": texto_situacional,
            "analisis_discursivo": analisis_discursivo,
        }
    )
