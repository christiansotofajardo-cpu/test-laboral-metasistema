from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uuid
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "metasistema-secret")
)

# =========================================================
# IPIP ITEMS (demo)
# =========================================================

IPIP_ITEMS = [
    {"id": "ipip_1", "text": "Soy una persona organizada y planificada.", "factor": "CON"},
    {"id": "ipip_2", "text": "Me preocupo por el bienestar de los demás.", "factor": "AGR"},
    {"id": "ipip_3", "text": "Me siento cómodo/a interactuando con otras personas.", "factor": "EXT"},
    {"id": "ipip_4", "text": "Mantengo la calma en situaciones difíciles.", "factor": "NEU"},
    {"id": "ipip_5", "text": "Me interesa aprender cosas nuevas.", "factor": "OPE"},
]

# =========================================================
# MEMORIA SIMPLE (EN RAM)
# =========================================================

RESULT_STORE = {}

# =========================================================
# RUTAS USUARIO
# =========================================================

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
    data = dict(form)

    texto_funcional = data.pop("texto_funcional", "")
    texto_situacional = data.pop("texto_situacional", "")

    scores = {"CON": 0, "AGR": 0, "EXT": 0, "NEU": 0, "OPE": 0}
    counts = {"CON": 0, "AGR": 0, "EXT": 0, "NEU": 0, "OPE": 0}

    for item in IPIP_ITEMS:
        if item["id"] in data:
            val = int(data[item["id"]])
            scores[item["factor"]] += val
            counts[item["factor"]] += 1

    avg_scores = {
        k: round(scores[k] / counts[k], 2) if counts[k] else None
        for k in scores
    }

    result_id = str(uuid.uuid4())

    RESULT_STORE[result_id] = {
        "avg_scores": avg_scores,
        "texto_funcional": texto_funcional,
        "texto_situacional": texto_situacional,
    }

    return templates.TemplateResponse(
        "submitted.html",
        {"request": request}
    )

# =========================================================
# RUTAS ADMIN (VERSIÓN 0)
# =========================================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_list(request: Request):
    return templates.TemplateResponse(
        "admin_list.html",
        {
            "request": request,
            "results": RESULT_STORE
        }
    )


@app.get("/admin/{result_id}", response_class=HTMLResponse)
async def admin_detail(request: Request, result_id: str):
    data = RESULT_STORE.get(result_id)

    if not data:
        return HTMLResponse("Evaluación no encontrada", status_code=404)

    return templates.TemplateResponse(
        "admin_detail.html",
        {
            "request": request,
            "result_id": result_id,
            "data": data
        }
    )
