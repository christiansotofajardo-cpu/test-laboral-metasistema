from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# -----------------------------
# Definición de ítems IPIP-100
# -----------------------------
# Cinco factores:
# - CON: Responsabilidad / escrupulosidad
# - NEU: Estabilidad emocional (bajo neuroticismo)
# - EXT: Extraversión
# - AGR: Amabilidad / cooperación
# - OPE: Apertura a la experiencia

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

# -----------------------------
# Rutas
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
async def submit_test(request: Request):

    # Leer datos del formulario
    form = await request.form()
    form_data = dict(form)

    # Extraer textos discursivos (si el template ya los tiene, se usan; si no, quedan vacíos y no pasa nada)
    texto_funcional = form_data.pop("texto_funcional", "").strip()
    texto_situacional = form_data.pop("texto_situacional", "").strip()

    # Acumuladores por factor
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

    # Calcular promedios
    avg_scores = {}
    for factor in scores.keys():
        if counts[factor] > 0:
            avg_scores[factor] = round(scores[factor] / counts[factor], 2)
        else:
            avg_scores[factor] = None

    # Placeholder análisis TRUNAJOD (no rompe nada aunque el template no lo use)
    analisis_discursivo = {
        "comentario_general": "Integración con TRUNAJOD pendiente en esta versión.",
        "texto_funcional_length": len(texto_funcional.split()) if texto_funcional else 0,
        "texto_situacional_length": len(texto_situacional.split()) if texto_situacional else 0,
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
