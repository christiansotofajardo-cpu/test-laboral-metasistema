from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any, Optional
import os
import statistics
import httpx
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ============================================================
# CONFIG
# ============================================================

TRUNAJOD_ENDPOINT = os.getenv("TRUNAJOD_ENDPOINT", "").strip()   # ej: https://tu-endpoint/trunajod
TRUNAJOD_API_KEY = os.getenv("TRUNAJOD_API_KEY", "").strip()
TRUNAJOD_TIMEOUT = float(os.getenv("TRUNAJOD_TIMEOUT", "25"))

# (Opcional) consignas internas para mostrar en el informe
CONSIGNA_FUNCIONAL = os.getenv("CONSIGNA_FUNCIONAL", "Tarea funcional (consigna no configurada).")
CONSIGNA_SITUACIONAL = os.getenv("CONSIGNA_SITUACIONAL", "Tarea situacional (consigna no configurada).")


# ============================================================
# IPIP-100 ITEMS (tal como lo tenías)
# ============================================================

IPIP_ITEMS: List[Dict] = [
    # CON – Responsabilidad / escrupulosidad (1–20)
    {"id": "item1", "text": "Planifico mi trabajo con anticipación.", "factor": "CON"},
    {"id": "item2", "text": "Termino las tareas que comienzo.", "factor": "CON"},
    {"id": "item3", "text": "Me esfuerzo por cumplir los plazos establecidos.", "factor": "CON"},
    {"id": "item4", "text": "Soy ordenado/a con mis materiales y espacios de trabajo.", "factor": "CON"},
    {"id": "item5", "text": "Reviso mi trabajo para evitar errores.", "factor": "CON"},
    {"id": "item6", "text": "Me considero responsable con mis compromisos laborales.", "factor": "CON"},
    {"id": "item7", "text": "Mantengo mis archivos y documentos organizados.", "factor": "CON"},
    {"id": "item8", "text": "Puedo concentrarme en una tarea sin distraerme fácilmente.", "factor": "CON"},
    {"id": "item9", "text": "Me gusta tener una rutina de trabajo clara.", "factor": "CON"},
    {"id": "item10", "text": "Hago más de lo que se espera de mí cuando es necesario.", "factor": "CON"},
    {"id": "item11", "text": "Cumplo mis promesas incluso cuando es incómodo.", "factor": "CON"},
    {"id": "item12", "text": "Prefiero hacer las cosas bien antes que rápido.", "factor": "CON"},
    {"id": "item13", "text": "Soy constante incluso cuando la tarea se vuelve aburrida.", "factor": "CON"},
    {"id": "item14", "text": "Me preparo con tiempo para reuniones o presentaciones.", "factor": "CON"},
    {"id": "item15", "text": "Al comenzar la jornada, organizo lo que haré en el día.", "factor": "CON"},
    {"id": "item16", "text": "Me cuesta dejar una tarea a medias.", "factor": "CON"},
    {"id": "item17", "text": "Sigo los procedimientos y protocolos establecidos.", "factor": "CON"},
    {"id": "item18", "text": "Tomo notas para no olvidar asuntos importantes.", "factor": "CON"},
    {"id": "item19", "text": "Cuando tengo muchas tareas, organizo mis prioridades.", "factor": "CON"},
    {"id": "item20", "text": "Me considero una persona confiable en el trabajo.", "factor": "CON"},

    # NEU – Estabilidad emocional (21–40)
    {"id": "item21", "text": "Mantengo la calma en situaciones de presión.", "factor": "NEU"},
    {"id": "item22", "text": "Puedo manejar bien el estrés laboral.", "factor": "NEU"},
    {"id": "item23", "text": "En conflictos, controlo mi tono de voz.", "factor": "NEU"},
    {"id": "item24", "text": "Cuando algo sale mal, recupero la tranquilidad rápidamente.", "factor": "NEU"},
    {"id": "item25", "text": "En general, me siento emocionalmente equilibrado/a.", "factor": "NEU"},
    {"id": "item26", "text": "Puedo recibir críticas sin descontrolarme.", "factor": "NEU"},
    {"id": "item27", "text": "Tiendo a ver las dificultades como desafíos manejables.", "factor": "NEU"},
    {"id": "item28", "text": "No me paralizo ante los problemas laborales.", "factor": "NEU"},
    {"id": "item29", "text": "Rara vez pierdo el control por enojo en el trabajo.", "factor": "NEU"},
    {"id": "item30", "text": "Me considero una persona resiliente.", "factor": "NEU"},
    {"id": "item31", "text": "En días difíciles, logro seguir funcionando adecuadamente.", "factor": "NEU"},
    {"id": "item32", "text": "Puedo separar mis emociones personales de las tareas laborales.", "factor": "NEU"},
    {"id": "item33", "text": "Cuando me equivoco, acepto el error y sigo adelante.", "factor": "NEU"},
    {"id": "item34", "text": "En emergencias, mantengo la cabeza fría.", "factor": "NEU"},
    {"id": "item35", "text": "En momentos de alta carga, priorizo sin angustiarme demasiado.", "factor": "NEU"},
    {"id": "item36", "text": "Suelo recuperar el ánimo después de un mal momento.", "factor": "NEU"},
    {"id": "item37", "text": "Mantengo una actitud serena frente a la incertidumbre.", "factor": "NEU"},
    {"id": "item38", "text": "No suelo exagerar los problemas laborales.", "factor": "NEU"},
    {"id": "item39", "text": "Me siento capaz de enfrentar cambios importantes en el trabajo.", "factor": "NEU"},
    {"id": "item40", "text": "Aunque sienta presión, rara vez me desbordo emocionalmente.", "factor": "NEU"},

    # EXT – Extraversión (41–60)
    {"id": "item41", "text": "Disfruto interactuar con otras personas en el trabajo.", "factor": "EXT"},
    {"id": "item42", "text": "Me resulta natural iniciar conversaciones con colegas.", "factor": "EXT"},
    {"id": "item43", "text": "Me siento cómodo/a hablando en reuniones laborales.", "factor": "EXT"},
    {"id": "item44", "text": "Me energiza trabajar en equipo.", "factor": "EXT"},
    {"id": "item45", "text": "Suelo participar activamente en discusiones grupales.", "factor": "EXT"},
    {"id": "item46", "text": "Disfruto conocer personas nuevas en contextos laborales.", "factor": "EXT"},
    {"id": "item47", "text": "Puedo presentar ideas frente a otros sin mucha dificultad.", "factor": "EXT"},
    {"id": "item48", "text": "Me siento cómodo/a rompiendo el hielo con desconocidos.", "factor": "EXT"},
    {"id": "item49", "text": "Me gusta compartir logros con el equipo.", "factor": "EXT"},
    {"id": "item50", "text": "Me motivan los ambientes laborales dinámicos.", "factor": "EXT"},
    {"id": "item51", "text": "Suelo tomar la palabra cuando es necesario.", "factor": "EXT"},
    {"id": "item52", "text": "Me acomoda liderar actividades o reuniones pequeñas.", "factor": "EXT"},
    {"id": "item53", "text": "Aporto comentarios durante las presentaciones de otros.", "factor": "EXT"},
    {"id": "item54", "text": "Busco espacios para conversar informalmente con colegas.", "factor": "EXT"},
    {"id": "item55", "text": "Comúnmente soy sociable en las pausas o descansos.", "factor": "EXT"},
    {"id": "item56", "text": "Me resulta fácil integrarme a nuevos grupos de trabajo.", "factor": "EXT"},
    {"id": "item57", "text": "Me siento cómodo/a expresando mis opiniones frente a superiores.", "factor": "EXT"},
    {"id": "item58", "text": "Disfruto colaborar con distintas áreas o equipos.", "factor": "EXT"},
    {"id": "item59", "text": "Me gusta participar en actividades sociales del trabajo.", "factor": "EXT"},
    {"id": "item60", "text": "Cuando el ambiente está muy silencioso, me agrada iniciar conversación.", "factor": "EXT"},

    # AGR – Amabilidad / cooperación (61–80)
    {"id": "item61", "text": "Trato a mis colegas con respeto incluso cuando no estoy de acuerdo.", "factor": "AGR"},
    {"id": "item62", "text": "Escucho con atención antes de responder.", "factor": "AGR"},
    {"id": "item63", "text": "Me esfuerzo por comprender el punto de vista de otros.", "factor": "AGR"},
    {"id": "item64", "text": "Evito hablar mal de mis compañeros a sus espaldas.", "factor": "AGR"},
    {"id": "item65", "text": "Ofrezco ayuda cuando veo que alguien lo necesita.", "factor": "AGR"},
    {"id": "item66", "text": "Busco soluciones que beneficien al equipo, no solo a mí.", "factor": "AGR"},
    {"id": "item67", "text": "Suelo ceder en cosas menores para evitar conflictos innecesarios.", "factor": "AGR"},
    {"id": "item68", "text": "Cuido mi forma de decir las cosas para no herir a otros.", "factor": "AGR"},
    {"id": "item69", "text": "Agradezco el trabajo de las demás personas.", "factor": "AGR"},
    {"id": "item70", "text": "Pido disculpas cuando me equivoco con alguien.", "factor": "AGR"},
    {"id": "item71", "text": "Soy paciente con las personas que aprenden más lento.", "factor": "AGR"},
    {"id": "item72", "text": "Intento mediar cuando hay tensiones en el equipo.", "factor": "AGR"},
    {"id": "item73", "text": "Respeto las diferencias de opinión y estilo.", "factor": "AGR"},
    {"id": "item74", "text": "Trato a todas las personas con la misma dignidad.", "factor": "AGR"},
    {"id": "item75", "text": "Me interesa mantener buenas relaciones laborales.", "factor": "AGR"},
    {"id": "item76", "text": "Reconozco el aporte de otros en los logros compartidos.", "factor": "AGR"},
    {"id": "item77", "text": "Evito reaccionar de forma agresiva en los desacuerdos.", "factor": "AGR"},
    {"id": "item78", "text": "Puedo negociar y llegar a acuerdos equilibrados.", "factor": "AGR"},
    {"id": "item79", "text": "Procuro ser justo/a cuando doy comentarios a otros.", "factor": "AGR"},
    {"id": "item80", "text": "Me importa que las personas se sientan tratadas con consideración.", "factor": "AGR"},

    # OPE – Apertura a la experiencia (81–100)
    {"id": "item81", "text": "Me interesa aprender nuevas formas de hacer mi trabajo.", "factor": "OPE"},
    {"id": "item82", "text": "Disfruto enfrentar tareas que representan un desafío intelectual.", "factor": "OPE"},
    {"id": "item83", "text": "Estoy dispuesto/a a probar nuevas herramientas o tecnologías.", "factor": "OPE"},
    {"id": "item84", "text": "Me gusta cuestionar los procedimientos para ver si se pueden mejorar.", "factor": "OPE"},
    {"id": "item85", "text": "Me atraen los proyectos innovadores.", "factor": "OPE"},
    {"id": "item86", "text": "Me siento cómodo/a trabajando con ideas abstractas o complejas.", "factor": "OPE"},
    {"id": "item87", "text": "Busco información adicional para entender mejor los temas.", "factor": "OPE"},
    {"id": "item88", "text": "Me gusta conectar ideas de distintas áreas.", "factor": "OPE"},
    {"id": "item89", "text": "Acepto cambios en la manera de trabajar cuando tienen sentido.", "factor": "OPE"},
    {"id": "item90", "text": "Me interesa escuchar propuestas diferentes a lo habitual.", "factor": "OPE"},
    {"id": "item91", "text": "Disfruto resolver problemas que no tienen una única respuesta correcta.", "factor": "OPE"},
    {"id": "item92", "text": "Me adapto bien a nuevas metodologías de trabajo.", "factor": "OPE"},
    {"id": "item93", "text": "Me gusta pensar en mejoras para los procesos existentes.", "factor": "OPE"},
    {"id": "item94", "text": "Estoy abierto/a a recibir feedback para cambiar mi forma de trabajar.", "factor": "OPE"},
    {"id": "item95", "text": "Siento curiosidad por entender cómo funcionan las cosas en mi organización.", "factor": "OPE"},
    {"id": "item96", "text": "Me informo sobre temas relacionados con mi área laboral.", "factor": "OPE"},
    {"id": "item97", "text": "Me motiva participar en capacitaciones o cursos.", "factor": "OPE"},
    {"id": "item98", "text": "Me interesa comprender el contexto amplio de las decisiones laborales.", "factor": "OPE"},
    {"id": "item99", "text": "Me resulta atractivo trabajar en ambientes que promueven la creatividad.", "factor": "OPE"},
    {"id": "item100", "text": "Estoy dispuesto/a a salir de mi zona de confort para aprender algo nuevo.", "factor": "OPE"},
]

FACTOR_LABELS = {
    "NEU": "Estabilidad emocional (bajo neuroticismo)",
    "CON": "Responsabilidad / escrupulosidad",
    "OPE": "Apertura a la experiencia",
    "AGR": "Amabilidad / cooperación",
    "EXT": "Extraversión",
}


# ============================================================
# TRUNAJOD CLIENT
# ============================================================

async def trunajod_analyze_text(texto: str) -> dict:
    """
    Llama a TRUNAJOD-Textual y devuelve:
    { ok: bool, data: dict, error: str|None }
    """
    texto = (texto or "").strip()
    if not texto:
        return {"ok": False, "data": {}, "error": "Texto vacío."}

    if not TRUNAJOD_ENDPOINT:
        return {"ok": False, "data": {}, "error": "TRUNAJOD_ENDPOINT no configurado."}

    headers = {"Content-Type": "application/json"}
    if TRUNAJOD_API_KEY:
        headers["Authorization"] = f"Bearer {TRUNAJOD_API_KEY}"

    payload = {"text": texto}

    try:
        async with httpx.AsyncClient(timeout=TRUNAJOD_TIMEOUT) as client:
            r = await client.post(TRUNAJOD_ENDPOINT, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            # Si el endpoint devuelve {data:{...}}, aplanamos
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
                data = data["data"]
            return {"ok": True, "data": data if isinstance(data, dict) else {}, "error": None}
    except Exception as e:
        return {"ok": False, "data": {}, "error": f"Fallo TRUNAJOD: {type(e).__name__}: {e}"}


# ============================================================
# SENSITIVE INDICES (robust extractor + scoring)
# ============================================================

def _norm_key(k: str) -> str:
    return (k or "").strip().lower().replace("_", " ").replace("|", " ").replace("  ", " ")

def _build_norm_map(d: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for k, v in (d or {}).items():
        out[_norm_key(str(k))] = v
    return out

def _get_float(norm_map: Dict[str, Any], possible_keys: List[str]) -> Optional[float]:
    for k in possible_keys:
        nk = _norm_key(k)
        if nk in norm_map:
            try:
                v = norm_map[nk]
                if v is None: 
                    continue
                return float(v)
            except Exception:
                continue
    return None

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def norm_0_100(x: Optional[float], lo: float, hi: float, invert: bool = False) -> Optional[int]:
    if x is None:
        return None
    if hi == lo:
        return 50
    v = (x - lo) / (hi - lo)
    v = clamp01(v)
    if invert:
        v = 1.0 - v
    return int(round(v * 100))

def mean_or_none(vals: List[Optional[int]]) -> Optional[int]:
    ok = [v for v in vals if v is not None]
    return int(round(statistics.mean(ok))) if ok else None

def extract_sensitive_indices(tru_data: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Extrae un set mínimo (sensible) usando los nombres reales.
    Soporta llaves con espacios / mayúsculas / variaciones.
    """
    nm = _build_norm_map(tru_data or {})

    # Coherencia / dispersión
    eg_pacc = _get_float(nm, ["EG local_coherence_PACC", "EG_local_coherence_PACC"])
    eg_pw   = _get_float(nm, ["EG local_coherence_PW", "EG_local_coherence_PW"])
    eg_pu   = _get_float(nm, ["EG local_coherence_PU", "EG_local_coherence_PU"])
    avg_cos = _get_float(nm, ["avg_cos_dist", "avg cos dist"])
    std_dist = _get_float(nm, ["std_distance", "std distance"])
    max_min_ratio = _get_float(nm, ["max_min_dist_ratio", "max min dist ratio"])

    # Relevancia (proxy TRU)
    sm_w2v = _get_float(nm, ["SM word2vec_sent_sim", "SM_word2vec_sent_sim"])
    sm_lex = _get_float(nm, ["SM lexical_overlap", "SM_lexical_overlap"])

    # Registro/Formalidad
    sp_lexden = _get_float(nm, ["SP Densidad Léxica", "SP_densidad_lexica"])
    sp_conn   = _get_float(nm, ["SP connecting words", "SP_connecting_words"])
    dm_all    = _get_float(nm, ["DM all types of discourse markers", "DM_all_types_of_discourse_markers"])
    dm_cause  = _get_float(nm, ["DM cause discourse markers", "DM_cause_discourse_markers"])
    gv_pron   = _get_float(nm, ["GV Pronoun density", "GV_pronoun_density"])
    sp_p12    = _get_float(nm, ["SP Densidad Número de 1,2 persona", "SP_densidad_numero_de_1,2_persona", "SP densidad numero de 1,2 persona"])
    sp_neg    = _get_float(nm, ["SP Densidad de negación", "SP_densidad_de_negacion"])

    # Desarrollo/Control
    mtld = _get_float(nm, ["TTR Diversidad léxica MTLD", "TTR_diversidad_lexica_MTLD", "MTLD"])
    sp_synsim = _get_float(nm, ["SP syntactic similarity", "SP_syntactic_similarity"])
    sp_sentlen = _get_float(nm, ["SP Promedio Longitud Oracion", "SP_promedio_longitud_oracion"])
    sp_clauselen = _get_float(nm, ["SP Promedio Longitud Cláusula", "SP_promedio_longitud_clausula"])
    sp_clauseden = _get_float(nm, ["SP Densidad de Cláusula", "SP_densidad_de_clausula"])

    # Emoción (alerta suave)
    neg = _get_float(nm, ["NEG"])
    pos = _get_float(nm, ["POS"])
    anger = _get_float(nm, ["anger"])
    fear  = _get_float(nm, ["fear"])

    return {
        "EG_local_coherence_PACC": eg_pacc,
        "EG_local_coherence_PW": eg_pw,
        "EG_local_coherence_PU": eg_pu,
        "avg_cos_dist": avg_cos,
        "std_distance": std_dist,
        "max_min_dist_ratio": max_min_ratio,

        "SM_word2vec_sent_sim": sm_w2v,
        "SM_lexical_overlap": sm_lex,

        "SP_densidad_lexica": sp_lexden,
        "SP_connecting_words": sp_conn,
        "DM_all_markers": dm_all,
        "DM_cause_markers": dm_cause,
        "GV_pronoun_density": gv_pron,
        "SP_12_person": sp_p12,
        "SP_negation_density": sp_neg,

        "MTLD": mtld,
        "SP_syntactic_similarity": sp_synsim,
        "SP_sentence_length": sp_sentlen,
        "SP_clause_length": sp_clauselen,
        "SP_clause_density": sp_clauseden,

        "NEG": neg,
        "POS": pos,
        "anger": anger,
        "fear": fear,
    }

def score_sensitive(text: str, idx: Dict[str, Optional[float]]) -> Dict[str, Any]:
    """
    Scoring TRUNAJOD-sensible por texto:
    - coherencia
    - relevancia (proxy TRU)
    - registro
    - desarrollo
    - alerta_emocion (suave)
    - global
    """
    words = (text or "").split()
    n_words = len(words)

    # ---------- Coherencia ----------
    # rangos heurísticos (ajustables tras datos reales)
    s_eg = mean_or_none([
        norm_0_100(idx.get("EG_local_coherence_PACC"), 0.20, 0.85, invert=False),
        norm_0_100(idx.get("EG_local_coherence_PW"),   0.20, 0.85, invert=False),
        norm_0_100(idx.get("EG_local_coherence_PU"),   0.20, 0.85, invert=False),
    ])
    s_cos = norm_0_100(idx.get("avg_cos_dist"), 0.15, 0.65, invert=True)  # menor dist = mejor
    s_std = norm_0_100(idx.get("std_distance"), 0.05, 0.35, invert=True)
    coherencia = mean_or_none([s_eg, s_cos, s_std])

    # ---------- Relevancia (proxy TRU) ----------
    s_w2v = norm_0_100(idx.get("SM_word2vec_sent_sim"), 0.15, 0.85, invert=False)
    s_lex = norm_0_100(idx.get("SM_lexical_overlap"),   0.05, 0.55, invert=False)
    relevancia = mean_or_none([s_w2v, s_lex])

    # ---------- Registro/Formalidad ----------
    # más léxico, más conectores, más marcadores; menos pronombres y menos 1-2 persona
    s_lexden = norm_0_100(idx.get("SP_densidad_lexica"), 0.30, 0.70, invert=False)
    s_conn   = norm_0_100(idx.get("SP_connecting_words"), 0.01, 0.08, invert=False)
    s_dm     = mean_or_none([
        norm_0_100(idx.get("DM_all_markers"), 0.00, 0.08, invert=False),
        norm_0_100(idx.get("DM_cause_markers"), 0.00, 0.03, invert=False),
    ])
    s_pron   = norm_0_100(idx.get("GV_pronoun_density"), 0.03, 0.18, invert=True)
    s_p12    = norm_0_100(idx.get("SP_12_person"), 0.00, 0.06, invert=True)
    registro = mean_or_none([s_lexden, s_conn, s_dm, s_pron, s_p12])

    # ---------- Desarrollo/Control ----------
    s_mtld  = norm_0_100(idx.get("MTLD"), 40, 140, invert=False)
    s_syn   = norm_0_100(idx.get("SP_syntactic_similarity"), 0.20, 0.85, invert=False)

    # Longitud: rango óptimo en tareas laborales (ajustable)
    if n_words >= 140:
        s_len = 95
    elif n_words >= 90:
        s_len = 85
    elif n_words >= 60:
        s_len = 70
    elif n_words >= 40:
        s_len = 55
    else:
        s_len = 35

    # cláusulas (señal de estructuración; no siempre más es mejor)
    s_clause = mean_or_none([
        norm_0_100(idx.get("SP_clause_density"), 0.10, 0.45, invert=False),
        norm_0_100(idx.get("SP_clause_length"),  6,  18,  invert=False),
    ])
    desarrollo = mean_or_none([s_mtld, s_syn, s_len, s_clause])

    # ---------- Emoción (alerta suave) ----------
    # No es diagnóstico; solo una señal operativa.
    neg = idx.get("NEG")
    anger = idx.get("anger")
    fear = idx.get("fear")
    s_neg = norm_0_100(neg, 0.10, 0.55, invert=True)  # más NEG -> peor (invertimos)
    s_ang = norm_0_100(anger, 0.00, 0.20, invert=True)
    s_fear = norm_0_100(fear, 0.00, 0.20, invert=True)
    alerta_emocion = mean_or_none([s_neg, s_ang, s_fear])

    # ---------- Global TRU-Sensible ----------
    # Ponderación: coherencia + relevancia mandan (tarea-específico)
    parts = []
    weights = []
    def add(x, w):
        if x is None:
            return
        parts.append(x)
        weights.append(w)

    add(coherencia, 0.35)
    add(relevancia, 0.35)
    add(registro,   0.15)
    add(desarrollo, 0.15)

    global_score = None
    if parts and weights:
        global_score = int(round(sum(p*w for p, w in zip(parts, weights)) / sum(weights)))

    # Niveles simples
    def nivel(x: Optional[int]) -> str:
        if x is None:
            return "No disponible"
        if x < 45:
            return "Bajo"
        if x < 70:
            return "Medio"
        return "Alto"

    return {
        "n_words": n_words,
        "coherencia": coherencia,
        "relevancia": relevancia,
        "registro": registro,
        "desarrollo": desarrollo,
        "alerta_emocion": alerta_emocion,
        "global": global_score,
        "niveles": {
            "coherencia": nivel(coherencia),
            "relevancia": nivel(relevancia),
            "registro": nivel(registro),
            "desarrollo": nivel(desarrollo),
            "global": nivel(global_score),
        }
    }


# ============================================================
# ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def show_test(request: Request):
    return templates.TemplateResponse("test.html", {"request": request, "items": IPIP_ITEMS})

@app.post("/test", response_class=HTMLResponse)
async def submit_test(request: Request):
    form = await request.form()
    form_data = dict(form)

    texto_funcional = form_data.pop("texto_funcional", "").strip()
    texto_situacional = form_data.pop("texto_situacional", "").strip()

    scores = {"NEU": 0, "CON": 0, "OPE": 0, "AGR": 0, "EXT": 0}
    counts = {"NEU": 0, "CON": 0, "OPE": 0, "AGR": 0, "EXT": 0}

    # Sumar puntajes IPIP
    for item in IPIP_ITEMS:
        item_id = item["id"]
        factor = item["factor"]
        if item_id in form_data and form_data[item_id] != "":
            try:
                value = int(form_data[item_id])
            except ValueError:
                value = 0
            scores[factor] += value
            counts[factor] += 1

    # Promedios
    avg_scores = {}
    for factor in scores.keys():
        avg_scores[factor] = round(scores[factor] / counts[factor], 2) if counts[factor] > 0 else None

    # -------------------------
    # TRUNAJOD + Índices sensibles
    # -------------------------
    tru_func = await trunajod_analyze_text(texto_funcional)
    tru_sit  = await trunajod_analyze_text(texto_situacional)

    idx_func = extract_sensitive_indices(tru_func.get("data", {})) if tru_func.get("ok") else extract_sensitive_indices({})
    idx_sit  = extract_sensitive_indices(tru_sit.get("data", {})) if tru_sit.get("ok") else extract_sensitive_indices({})

    score_func = score_sensitive(texto_funcional, idx_func)
    score_sit  = score_sensitive(texto_situacional, idx_sit)

    # Score global combinado (funcional + situacional)
    combined_global = None
    fg = score_func.get("global")
    sg = score_sit.get("global")
    if fg is not None and sg is not None:
        combined_global = int(round((fg + sg) / 2))
    elif fg is not None:
        combined_global = fg
    elif sg is not None:
        combined_global = sg

    analisis_discursivo = {
        "meta": {
            "version": "TestLaboral_TRU_Sensible_v1",
            "timestamp": datetime.utcnow().isoformat(),
            "trunajod_endpoint_configurado": bool(TRUNAJOD_ENDPOINT),
            "trunajod_ok_funcional": tru_func.get("ok", False),
            "trunajod_ok_situacional": tru_sit.get("ok", False),
            "trunajod_error_funcional": tru_func.get("error"),
            "trunajod_error_situacional": tru_sit.get("error"),
        },
        "consignas": {
            "funcional": CONSIGNA_FUNCIONAL,
            "situacional": CONSIGNA_SITUACIONAL,
        },
        "trunajod_raw": {
            "funcional": tru_func.get("data", {}),
            "situacional": tru_sit.get("data", {}),
        },
        "indices_sensibles": {
            "funcional": idx_func,
            "situacional": idx_sit,
        },
        "scores_sensibles": {
            "funcional": score_func,
            "situacional": score_sit,
            "global_promedio": combined_global,
        }
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
