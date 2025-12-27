from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from typing import Dict, Any
import os
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ============================================================
# SESSION
# ============================================================

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "metasistema-secret-key")
)

# ============================================================
# MEMORIA EN EL SISTEMA
# ============================================================

RESULT_STORE: Dict[str, Dict[str, Any]] = {}

# ============================================================
# CONFIG
# ============================================================

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# ============================================================
# IPIP ITEMS (DEMO FUNCIONAL)
# 👉 Puedes reemplazar esta lista por el IPIP-100 completo cuando quieras
# ============================================================

IPIP_ITEMS = [
    {"id": "ipip_1", "text": "Soy una persona organizada y planificada.", "factor": "CON"},
    {"id": "ipip_2", "text": "Me preocupo por el bienestar de los demás.", "factor": "AGR"},
    {"id": "ipip_3", "text": "Me siento cómodo/a interactuando con otras personas.", "factor": "EXT"},
    {"id": "ipip_4", "text": "Mantengo la calma en situaciones difíciles.", "factor": "NEU"},
    {"id": "ipip_5", "text": "Me interesa aprender cosas nuevas.", "factor": "OPE"},
]

# ============================================================
# FUNCIONES SIMPLIFICADAS (DEMO)
# ============================================================

def extract_sensitive_indices(_data: dict) -> dict:
    return {"dummy": 1}

def score_sensitive(text: str, _indices: dict) -> dict:
    length_score = min(len(text) // 20, 100)
    return {
        "global": length_score,
        "coherencia": length_score,
        "relevancia": length_score,
        "registro": length_score,
        "desarrollo": length_score,
    }

def generar_reporte_metasistema(
    avg_scores,
    score_func,
    score_sit,
    combined_global,
    tru_ok_func=True,
    tru_ok_sit=True,
):
    return {
        "perfil_general": {
            "global": combined_global,
            "funcional": score_func.get("global"),
            "situacional": score_sit.get("global"),
        },
        "ipip": avg_scores,
        "mensaje": "Reporte generado correctamente (modo demo).",
    }

# ============================================================
# HELPERS
# ============================================================

def require_admin(request: Request):
    if not request.session.get("admin"):
        return RedirectResponse("/admin/login", status_code=302)

# ============================================================
# ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/test", response_class=HTMLResponse)
async def show_test(request: Request):
    return templates.TemplateResponse(
        "test.html",
        {"request": request, "items": IPIP_ITEMS}
    )


@app.post("/test", response_class=HTMLResponse)
async def submit_test(request: Request):
    form = await request.form()
    form_data = dict(form)

    texto_funcional = form_data.pop("texto_funcional", "")
    texto_situacional = form_data.pop("texto_situacional", "")

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

    score_func = score_sensitive(texto_funcional, {})
    score_sit = score_sensitive(texto_situacional, {})
    combined_global = int((score_func["global"] + score_sit["global"]) / 2)

    reporte = generar_reporte_metasistema(
        avg_scores=avg_scores,
        score_func=score_func,
        score_sit=score_sit,
        combined_global=combined_global,
    )

    result_id = str(uuid.uuid4())

    RESULT_STORE[result_id] = {
        "reporte": reporte,
        "avg_scores": avg_scores,
    }

    return templates.TemplateResponse(
        "submitted.html",
        {"request": request}
    )

# ============================================================
# ADMIN
# ============================================================

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form(request: Request):
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": None}
    )

@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        request.session["admin"] = True
        return RedirectResponse("/admin/result-list", status_code=302)

    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Credenciales incorrectas"}
    )

@app.get("/admin/result-list", response_class=HTMLResponse)
async def admin_list(request: Request):
    auth = require_admin(request)
    if auth:
        return auth

    return HTMLResponse(
        "<h3>Resultados disponibles:</h3><ul>" +
        "".join(
            f'<li><a href="/admin/result/{rid}">{rid}</a></li>'
            for rid in RESULT_STORE.keys()
        ) +
        "</ul>"
    )

@app.get("/admin/result/{result_id}", response_class=HTMLResponse)
async def admin_result(request: Request, result_id: str):
    auth = require_admin(request)
    if auth:
        return auth

    data = RESULT_STORE.get(result_id)
    if not data:
        return HTMLResponse("<h3>Resultado no encontrado</h3>", status_code=404)

    data["request"] = request
    return templates.TemplateResponse("result.html", data)
