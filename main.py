from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from typing import Dict, Any
import os
import httpx
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

TRUNAJOD_ENDPOINT = os.getenv("TRUNAJOD_ENDPOINT", "").strip()
TRUNAJOD_API_KEY = os.getenv("TRUNAJOD_API_KEY", "").strip()
TRUNAJOD_TIMEOUT = float(os.getenv("TRUNAJOD_TIMEOUT", "25"))

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

SHOW_TECHNICAL = os.getenv("SHOW_TECHNICAL", "0") in ("1", "true", "True")

# ============================================================
# IPIP_ITEMS
# ============================================================
# ⚠️ PEGAR AQUÍ TU IPIP_ITEMS ORIGINAL (SIN CAMBIOS)

# ============================================================
# TRUNAJOD CLIENT
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
# ============================================================
# ⚠️ PEGAR AQUÍ, ÍNTEGROS:
# extract_sensitive_indices
# score_sensitive
# generar_reporte_metasistema

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

    texto_funcional = form_data.pop("texto_funcional", "").strip()
    texto_situacional = form_data.pop("texto_situacional", "").strip()

    # ---------------- IPIP ----------------
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

    # ---------------- TRUNAJOD ----------------
    tru_func = await trunajod_analyze_text(texto_funcional)
    tru_sit = await trunajod_analyze_text(texto_situacional)

    idx_func = extract_sensitive_indices(tru_func["data"]) if tru_func["ok"] else {}
    idx_sit = extract_sensitive_indices(tru_sit["data"]) if tru_sit["ok"] else {}

    score_func = score_sensitive(texto_funcional, idx_func)
    score_sit = score_sensitive(texto_situacional, idx_sit)

    fg = score_func.get("global")
    sg = score_sit.get("global")
    combined_global = int(round((fg + sg) / 2)) if fg and sg else fg or sg

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

    return templates.TemplateResponse(
        "submitted.html",
        {"request": request}
    )

# ============================================================
# ADMIN LOGIN
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
        return RedirectResponse("/admin/dashboard", status_code=302)

    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Credenciales incorrectas"}
    )


@app.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=302)

# ============================================================
# ADMIN RESULT
# ============================================================

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
