import os
from fastapi.templating import Jinja2Templates


def _resolve_templates_dir() -> str:
    """Resolver ruta de templates compatible con Docker y entorno local."""
    # Orden de candidatos: variable de entorno, ruta Docker, rutas locales relativas
    candidates = [
        os.environ.get("TEMPLATES_DIR"),
        "/app/src/templates",
        os.path.join(os.getcwd(), "src", "templates"),
        os.path.join(os.path.dirname(__file__), "..", "..", "templates"),
    ]

    for path in candidates:
        if path and os.path.isdir(path):
            return os.path.abspath(path)

    # Fallback: usar ruta relativa estándar aunque no exista (FastAPI lanzará error claro)
    return os.path.abspath(os.path.join(os.getcwd(), "src", "templates"))


def get_templates() -> Jinja2Templates:
    """Obtener instancia de Jinja2Templates con auto_reload y ruta resuelta."""
    templates_dir = _resolve_templates_dir()
    return Jinja2Templates(directory=templates_dir, auto_reload=True)


