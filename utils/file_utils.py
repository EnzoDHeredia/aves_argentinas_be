import json
from config import logger

def load_json(path):
    """Carga un archivo JSON de forma segura"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando {path}: {e}")
        return None
