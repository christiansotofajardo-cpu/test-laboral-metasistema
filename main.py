from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uuid
import os
import io

# =========================================================
# PDF EXPORT (ADD-ON)
# =========================================================
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

# =========================================================
# Intento seguro de matplotlib (no botar deploy)
# =========================================================
MATPLOTLIB_OK = True
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:
    MATPLOTLIB_OK = False
    plt = None

# =========================================================
# APP BASE
# =========================================================
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
# MEMORIA SIMPLE (RAM)
# =========================================================
RESULT_STORE = {}

# =========================================================
# ACTIVADORES LINGÜÍSTICOS – TEST LABORAL 6.0
# =========================================================
ACTIVADORES = {
    "A": {
        "keywords": [
            "yo", "resuelvo", "resolv", "actúo", "actuo", "actuar",
            "decido", "ejecuto", "me hago cargo", "me encargo",
            "soluciono", "lo hago"
        ],
        "explicacion": (
            "El texto muestra una estrategia comunicativa centrada en la acción directa "
            "y la iniciativa personal como principal vía de resolución de la situación planteada."
        )
    },
    "B": {
        "keywords": [
            "jefe", "supervisor", "encargado", "informo", "consulto",
            "derivo", "escalo", "protocolo", "procedimiento",
            "normativa", "reglamento", "reporto", "rrhh",
            "recursos humanos"
        ],
        "explicacion": (
            "El texto muestra una estrategia comunicativa orientada a la derivación jerárquica "
            "y al uso de la estructura organizacional como principal recurso para abordar la situación."
        )
    },
    "C": {
        "keywords": [
            "equipo", "personas", "converso", "conversar", "dialogo",
            "diálogo", "apoyo", "apoyar", "escucho", "escuchar",
            "mediar", "contener", "clima", "emocional",
            "acuerdo", "vínculo", "vinculo"
        ],
        "explicacion": (
            "El texto muestra una estrategia comunicativa centrada en el vínculo interpersonal "
            "y el cuidado del clima relacional como forma principal de abordar la situación planteada."
        )
    }
}

# =========================================================
# LÓGICA 6.0
# =========================================================
def _count_matches(texto: str, keywords: list[str]) -> int:
    texto = (texto or "").lower().strip()
    if not texto:
        return 0
    return sum(1 for kw in keywords if kw in texto)

def detectar_variante_situacional(texto_situacional: str) -> dict:
    conteos = {
        k: _count_matches(texto_situacional, v["keywords"])
        for k, v in ACTIVADORES.items()
    }

    variante_key = max(conteos, key=conteos.get)
    if conteos[variante_key] == 0:
        variante_key = "B"  # fallback ético

    return {
        "variante": f"MEDIO–{variante_key}",
        "explicacion": ACTIVADORES[variante_key]["explicacion"],
        "conteos": conteos
    }

# =========================================================
# GRÁFICOS (PYTHON)
# =========================================================
def _placeholder_png() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc``\x00"
        b"\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )

def _plot_bar_png(labels, values, title: str) -> bytes:
    if not MATPLOTLIB_OK or plt is None:
        return _placeholder_png()

    fig = plt.figure(figsize=(7, 3), dpi=150)
    ax = fig.add_subplot(111)
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_ylim(0, max(values) + 0.5 if values else 1)

    for i, v in enumerate(values):
        ax.text(i, float(v) + 0.05, str(v), ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

# =========================================================
# RUTAS USUARIO
# =========================================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def show_test(request: Request):
    return templates.TemplateResponse("test.html", {"request": request, "items": IPIP_ITEMS})

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
        k: round(scores[k] / counts[k], 2) if counts[k] else 0
        for k in scores
    }

    result_id = str(uuid.uuid4())
    meta_6 = detectar_variante_situacional(texto_situacional)

    RESULT_STORE[result_id] = {
        "avg_scores": avg_scores,
        "texto_funcional": texto_funcional,
        "texto_situacional": texto_situacional,
        "meta_6": meta_6
    }

    return templates.TemplateResponse("submitted.html", {"request": request})

# =========================================================
# RUTAS ADMIN
# =========================================================
@app.get("/admin", response_class=HTMLResponse)
async def admin_list(request: Request):
    return templates.TemplateResponse(
        "admin_list.html", {"request": request, "results": RESULT_STORE}
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
            "data": data,
            "matplotlib_ok": MATPLOTLIB_OK
        }
    )

# =========================================================
# ENDPOINTS DE IMÁGENES
# =========================================================
@app.get("/admin/{result_id}/ipip.png")
async def admin_ipip_png(result_id: str):
    data = RESULT_STORE.get(result_id)
    if not data:
        return Response(status_code=404)

    labels = ["CON", "AGR", "EXT", "NEU", "OPE"]
    values = [data["avg_scores"].get(k, 0) for k in labels]
    png = _plot_bar_png(labels, values, "IPIP – Promedios por factor")
    return Response(content=png, media_type="image/png")

@app.get("/admin/{result_id}/activadores.png")
async def admin_activadores_png(result_id: str):
    data = RESULT_STORE.get(result_id)
    if not data:
        return Response(status_code=404)

    conteos = data["meta_6"]["conteos"]
    labels = ["A", "B", "C"]
    values = [conteos.get(k, 0) for k in labels]
    png = _plot_bar_png(labels, values, "Activadores discursivos (tarea situacional)")
    return Response(content=png, media_type="image/png")

# =========================================================
# EXPORT PDF (ADD-ON FINAL)
# =========================================================
@app.get("/admin/{result_id}/pdf")
async def admin_pdf(request: Request, result_id: str):
    data = RESULT_STORE.get(result_id)
    if not data:
        return Response("Evaluación no encontrada", status_code=404)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("admin_detail.html")

    html_content = template.render(
        request=request,
        result_id=result_id,
        data=data,
        matplotlib_ok=MATPLOTLIB_OK
    )

    pdf = HTML(string=html_content).write_pdf()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename=\"reporte_{result_id}.pdf\"'
        }
    )
