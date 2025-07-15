from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import torch

# Importaciones locales
from config import THRESHOLD, MAX_CONTENT_LENGTH, logger, CLASSES_PATH, EBIRD_TAXONOMY_PATH, NOMBRE_COMUN_PATH, IMAGES_PATH
from utils import load_json
from models import BirdClassifier
from services import BirdService, ImageProcessor, ImageGalleryService, EBirdService

# Configuración del dispositivo
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Cargar datos
CLASSES = load_json(CLASSES_PATH)
if CLASSES is None:
    raise RuntimeError(f"No se pudo cargar {CLASSES_PATH}")

EBIRD_TAXONOMY = load_json(EBIRD_TAXONOMY_PATH)
if EBIRD_TAXONOMY is None:
    raise RuntimeError(f"No se pudo cargar {EBIRD_TAXONOMY_PATH}")

CIENTIFICO_A_NOMBRE_COMUN = load_json(NOMBRE_COMUN_PATH)
if CIENTIFICO_A_NOMBRE_COMUN is None:
    raise RuntimeError(f"No se pudo cargar {NOMBRE_COMUN_PATH}")

# Inicializar servicios
bird_classifier = BirdClassifier(DEVICE, len(CLASSES))
image_processor = ImageProcessor(DEVICE)
bird_service = BirdService(CLASSES, EBIRD_TAXONOMY, CIENTIFICO_A_NOMBRE_COMUN)
image_gallery_service = ImageGalleryService(IMAGES_PATH)
ebird_service = EBirdService()

# Configurar Flask
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para clasificación de aves"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    try:
        file = request.files['file']
        img = Image.open(file.stream).convert('RGB')
        
        # Procesar imagen y predecir
        tensor = image_processor.preprocess_image(img)
        pred_idx, confidence = bird_classifier.predict(tensor)

        if confidence < THRESHOLD:
            return jsonify({
                'class': "no se identifica ave",
                'confidence': confidence,
                'ebird_info': None,
                'sexo': None,
                'nombre_comun': None,
                'species_code': None
            })

        # Extraer información completa
        predicted_class = bird_service.get_class_name(pred_idx)
        sexo, nombre_comun, ebird_info = bird_service.extraer_info_completa(predicted_class)
        ebird_info_filtrado = bird_service.filter_ebird_info(ebird_info)

        # Extraer el species_code de la información de eBird
        species_code = ebird_info.get('speciesCode') if ebird_info else None

        response = {
            'class': predicted_class,
            'idx': pred_idx,
            'confidence': confidence,
            'ebird_info': ebird_info_filtrado,
            'sexo': sexo,
            'nombre_comun': nombre_comun,
            'species_code': species_code
        }

        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        return jsonify({'error': 'Error procesando la imagen'}), 500

@app.route('/<int:idx>', methods=['GET'])
def get_images(idx):
    images = image_gallery_service.get_images_by_idx(idx)
    return jsonify(images)

@app.route('/images/<path:filename>')
def serve_image(filename):
    from flask import send_from_directory
    return send_from_directory(IMAGES_PATH, filename)

@app.route('/observations/<species_code>', methods=['GET'])
def get_observations(species_code):
    """Endpoint para obtener observaciones recientes de una especie"""
    try:
        if not species_code:
            return jsonify({'error': 'species_code es requerido'}), 400
            
        # Obtener observaciones de eBird
        observations = ebird_service.get_recent_observations(species_code, max_results=15)
        
        return jsonify({
            'species_code': species_code,
            'observations': observations,
            'total_count': len(observations)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo observaciones para {species_code}: {e}")
        return jsonify({'error': 'Error obteniendo observaciones'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)