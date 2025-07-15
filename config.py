import os
import logging

# Configuración del modelo
IMG_SIZE = (224, 224)
THRESHOLD = 0.65

# Rutas de archivos
MODEL_PATH = os.environ.get('MODEL_PATH', 'model/modelo_102_B1_v1.1.pth')
EBIRD_TAXONOMY_PATH = os.environ.get('EBIRD_TAXONOMY_PATH', 'data/ebird_taxonomy.json')
CLASSES_PATH = os.environ.get('CLASSES_PATH', 'data/classes.json')
NOMBRE_COMUN_PATH = os.environ.get('NOMBRE_COMUN_PATH', 'data/cientifico_a_nombre_comun.json')

# Configuración de imágenes
IMAGES_PATH = os.environ.get('IMAGES_PATH', 'images')

# Configuración Flask
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

# Configuración de logging
def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

logger = setup_logging()
