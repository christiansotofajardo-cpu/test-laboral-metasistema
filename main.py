from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import os
import httpx
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ============================================================
# MEMORIA EN EL SISTEMA (IN-MEMORY)
# ============================================================

RESULT_STORE: Dict[str, Dict[str, Any]] = {}

# ============================================================
# CONFIGURACIÓN
# ============================================================

TRUNAJOD_ENDPOINT = os.getenv("TRUNAJOD_ENDPOINT", "").strip()
TRUNAJOD_API_KEY = os.getenv("TRUNAJOD_API_KEY", "").strip()
TRUNAJOD_TIMEOUT = float(os.getenv("TRUNAJOD_TIMEOUT", "25"))

SHOW_TECHNICAL = os.getenv("SHOW_TECHNICAL", "0") in ("1", "true", "True")

CONSIGNA_FUNCIONAL = (
    "Imagina que te incorporas a una organización. "
    "Describe qué tipo de aporte profesional realizas habitualmente."
)

CONSIGNA_SITUACIONAL = (
    "Piensa en una situación laboral compleja o desafiante. "
    "Describe cómo la enfrentarías y qué harías para resolverla."
)

# ============================================================
# IPIP_ITEMS  (COPIAR ÍNTEGRO DESDE TU VERSIÓN ORIGINAL)
# ============================================================
# IPIP_ITEMS = [...]

# ============================================================
# TRUNAJOD CLIENT (IGUAL QUE ANTES)
# ============================================================

async def trunajod_analyze_text(texto: str) -> dict:
    texto = (texto or "").strip()
    if not texto:
        return {"ok": False, "data": {}, "error": "Texto vacío"}

    if not TRUNAJOD_ENDPOINT:
        return {"ok": False, "data": {}, "error": "TRUNAJOD_ENDPOINT no configurado"}

    headers = {"Content-Type": "application/json"}
    if TRUNAJOD_API_KEY:
        headers["Authorization"] = f"Bearer {TRUNAJOD_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=TRUNAJOD_TIMEOUT) as client:
            r = await client.post(TRUNAJOD_ENDPOINT, headers=headers, json={"text": texto})
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict) and "data" in data:
                data = data["data"]
            return {"ok": True, "data": data, "error": None}
    except Exception as e:
        return {"ok": False, "data": {}, "error": str(e)}

# ============================================================
# ÍNDICES + SCORING + REPORTE
# (COPIAR ÍNTEGROS DESDE TU VERSIÓN ORIGINAL)
# ============================================================

# extract_sensitive_indices(...)
# score_sensitive(...)
# generar_reporte_metasistema(...)

# ============================================================
# RUTAS
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/test", response_class=HTMLResponse)
async def show_test(request: Request):
    return templates.TemplateResponse(
        "test.html",
        {
            "request": request,
            "items": IPIP_ITEMS,
            "consigna_funcional": CONSIGNA_FUNCIONAL,
            "consigna_situacional": CONSIGNA_SITUACIONAL,
        },
    )


@app.post("/test", response_class=HTMLResponse)
async def submit_test(request: Request):
    form = await request.form()
    form_data = dict(form)

    texto_funcional = form_data.pop("texto_funcional", "").strip()
    texto_situacional = form_data.pop("texto_situacional", "").strip()

    # -------------------------------
    # IPIP SCORING (IGUAL QUE ANTES)
    # -------------------------------
    scores = {"NEU": 0, "CON": 0, "OPE": 0, "AGR": 0, "EXT": 0}
    counts = {"NEU": 0, "CON": 0, "OPE": 0, "AGR": 0, "EXT": 0}

    for item in IPIP_ITEMS:
        iid = item["id"]
        factor = item["factor"]
        if iid in form_data and form_data[iid]:
            val = int(form_data[iid])
            scores[factor] += val
            counts[factor] += 1

    avg_scores = {
        f: round(scores[f] / counts[f], 2) if counts[f] > 0 else None
        for f in scores
    }

    # -------------------------------
    # TRUNAJOD + ÍNDICES
    # -------------------------------
    tru_func = await trunajod_analyze_text(texto_funcional)
    tru_sit = await trunajod_analyze_text(texto_situacional)

    idx_func = extract_sensitive_indices(tru_func["data"]) if tru_func["ok"] else {}
    idx_sit = extract_sensitive_indices(tru_sit["data"]) if tru_sit["ok"] else {}

    score_func = score_sensitive(texto_funcional, idx_func)
    score_sit = score_sensitive(texto_situacional, idx_sit)

    fg = score_func.get("global")
    sg = score_sit.get("global")
    combined_global = int(round((fg + sg) / 2)) if fg and sg else fg or sg

    # -------------------------------
    # REPORTE METASISTEMA
    # -------------------------------
    reporte = generar_reporte_metasistema(
        avg_scores=avg_scores,
        score_func=score_func,
        score_sit=score_sit,
        combined_global=combined_global,
        tru_ok_func=tru_func["ok"],
        tru_ok_sit=tru_sit["ok"],
    )

    result_id = str(uuid.uuid4())

    RESULT_STORE[result_id] = {
        "request": request,
        "reporte": reporte,
        "analisis_discursivo": {
            "scores_sensibles": {
                "funcional": score_func,
                "situacional": score_sit,
                "global_promedio": combined_global,
            }
        },
        "avg_scores": avg_scores,
        "show_technical": SHOW_TECHNICAL,
    }

    # USUARIO NO VE RESULTADOS
    return templates.TemplateResponse(
        "submitted.html",
        {"request": request}
    )


# ============================================================
# ADMIN — VER RESULTADOS
# ============================================================

@app.get("/admin/result/{result_id}", response_class=HTMLResponse)
async def admin_result(request: Request, result_id: str):
    data = RESULT_STORE.get(result_id)
    if not data:
        return HTMLResponse("<h3>Resultado no encontrado</h3>", status_code=404)

    data["request"] = request
    return templates.TemplateResponse("result.html", data)
