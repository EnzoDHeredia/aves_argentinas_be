from utils import normalizar_nombre, extraer_nombre_cientifico
from config import logger

class BirdService:
    def __init__(self, classes, ebird_taxonomy, cientifico_a_nombre_comun):
        self.classes = classes
        self.idx_to_class = {i: name for i, name in enumerate(classes)}
        self.cientifico_a_nombre_comun = cientifico_a_nombre_comun
        
        # Crear diccionario eBird normalizado
        self.ebird_sci_to_info = {
            normalizar_nombre(bird['sciName']): {
                'speciesCode': bird.get('speciesCode'),
                'comName': bird.get('comName'),
                'sciName': bird.get('sciName'),
                'category': bird.get('category'),
                'order': bird.get('order'),
                'familyComName': bird.get('familyComName'),
                'familySciName': bird.get('familySciName'),
            } for bird in ebird_taxonomy
        }
        
        logger.info(f"Servicio de aves inicializado - {len(self.classes)} clases, {len(self.ebird_sci_to_info)} especies eBird")
    
    def extraer_info_completa(self, nombre_clase):
        """Extrae toda la información de una clase: científico, sexo, común y eBird"""
        # Extraer nombre base y sexo
        partes = nombre_clase.split('.', 1)
        nombre = partes[1] if len(partes) == 2 else nombre_clase
        
        partes_nombre = nombre.split('_')
        sexo = partes_nombre[-1] if partes_nombre[-1] in ['macho', 'hembra'] else None
        
        # Obtener nombre científico usando la función existente
        nombre_cientifico = extraer_nombre_cientifico(nombre_clase, self.ebird_sci_to_info)
        
        # Extraer el nombre científico de la clase para buscar en el mapping
        nombre_cientifico_para_busqueda = self._extraer_nombre_cientifico_de_clase(nombre)
        
        # Buscar nombre común usando el nombre científico
        nombre_comun = None
        if nombre_cientifico_para_busqueda:
            nombre_comun = self.cientifico_a_nombre_comun.get(nombre_cientifico_para_busqueda)
        
        # Si no encuentra, intentar con el nombre científico normalizado
        if nombre_comun is None and nombre_cientifico:
            nombre_cientifico_normalizado = nombre_cientifico.replace(' ', '_').lower()
            nombre_comun = self.cientifico_a_nombre_comun.get(nombre_cientifico_normalizado)
        
        # Si aún no encuentra, usar la lógica original como fallback
        if nombre_comun is None:
            nombre_para_busqueda = '_'.join(partes_nombre[:-1] if sexo else partes_nombre)
            nombre_comun = self.cientifico_a_nombre_comun.get(nombre_para_busqueda)
            
            # Si no encuentra, intentar con diferentes combinaciones
            if nombre_comun is None:
                # Intentar con las últimas dos partes (nombre científico)
                if len(partes_nombre) >= 2:
                    nombre_alt2 = '_'.join(partes_nombre[-2:])
                    nombre_comun = self.cientifico_a_nombre_comun.get(nombre_alt2)
                    
                # Como último recurso, buscar cualquier clave que contenga partes del nombre
                if nombre_comun is None:
                    for clave in self.cientifico_a_nombre_comun.keys():
                        if any(parte in clave for parte in partes_nombre[:2]):
                            nombre_comun = self.cientifico_a_nombre_comun[clave]
                            break
        
        # Obtener información de eBird
        nombre_normalizado = normalizar_nombre(nombre_cientifico) if nombre_cientifico else None
        if nombre_normalizado:
            ebird_info = self.ebird_sci_to_info.get(nombre_normalizado, {})
        else:
            ebird_info = {}
        
        return sexo, nombre_comun, ebird_info
    
    def get_class_name(self, pred_idx):
        """Obtiene el nombre de la clase por índice"""
        return self.idx_to_class.get(pred_idx, "Clase desconocida")
    
    def filter_ebird_info(self, ebird_info):
        """Filtra la información relevante de eBird"""
        if not ebird_info:
            return None
            
        return {
            'comName': ebird_info.get('comName'),
            'sciName': ebird_info.get('sciName'),
            'familyComName': ebird_info.get('familyComName'),
            'order': ebird_info.get('order'),
            'category': ebird_info.get('category'),
        }
    
    def _extraer_nombre_cientifico_de_clase(self, nombre_clase):
        """Extrae solo el nombre científico de una clase que puede contener nombre común + científico"""
        partes = nombre_clase.split('_')
        
        # Si la clase tiene el formato: nombre_comun_genus_species
        # Buscar dónde empieza el nombre científico (típicamente las últimas 2 partes)
        if len(partes) >= 2:
            # Las últimas dos partes probablemente sean genus_species
            posible_cientifico = '_'.join(partes[-2:])
            
            # Verificar si existe en el mapping
            if posible_cientifico in self.cientifico_a_nombre_comun:
                return posible_cientifico
            
            # Si no, probar con diferentes combinaciones
            for i in range(len(partes) - 1, 0, -1):
                if i + 1 < len(partes):
                    posible = '_'.join(partes[i:i+2])
                    if posible in self.cientifico_a_nombre_comun:
                        return posible
        
        return None

    def extraer_sexo_y_nombres(self, nombre_clase):
        """Extrae el sexo y los nombres común y científico de una clase"""
        # Intentar primero con el método completo
        sexo, nombre_comun, ebird_info = self.extraer_info_completa(nombre_clase)
        
        # Si no se encontró sexo, intentar con el método alternativo
        if sexo is None:
            nombre_cientifico = self._extraer_nombre_cientifico_de_clase(nombre_clase)
            nombre_comun = self.cientifico_a_nombre_comun.get(nombre_cientifico)
            
            # Asumir sexo basado en el nombre de la clase
            partes_nombre = nombre_clase.split('_')
            sexo = partes_nombre[-1] if partes_nombre[-1] in ['macho', 'hembra'] else None
        
        return sexo, nombre_comun, ebird_info
