import unicodedata

def normalizar_nombre(nombre):
    """Normaliza nombres científicos removiendo acentos y estandarizando formato"""
    nombre = nombre.lower().replace('_', ' ').strip()
    # Remover acentos
    nombre = ''.join(c for c in unicodedata.normalize('NFD', nombre) 
                    if unicodedata.category(c) != 'Mn')
    return ' '.join(nombre.split())

def extraer_nombre_cientifico(nombre_clase, ebird_dict):
    """Extrae el nombre científico de una clase del modelo"""
    # Mapeo de nomenclatura antigua a moderna
    mapeo_nomenclatura = {
        'phalacrocorax brasilianus': 'nannopterum brasilianum',
        # Agregar más mapeos aquí si es necesario
    }
    
    partes = nombre_clase.replace('.', ' ').replace('_', ' ').split()
    
    # Probar todas las combinaciones de dos palabras consecutivas
    for i in range(len(partes) - 1):
        candidato = f"{partes[i]} {partes[i+1]}"
        
        # Verificar si necesita mapeo de nomenclatura
        candidato_mapeado = mapeo_nomenclatura.get(candidato.lower(), candidato)
        
        if normalizar_nombre(candidato_mapeado) in ebird_dict:
            return candidato_mapeado
    
    # Si no encuentra, devolver las dos primeras palabras alfabéticas
    palabras_latinas = [p for p in partes if p.isalpha()]
    if len(palabras_latinas) >= 2:
        candidato = f"{palabras_latinas[0]} {palabras_latinas[1]}"
        # Aplicar mapeo también aquí
        return mapeo_nomenclatura.get(candidato.lower(), candidato)
    
    return nombre_clase.replace('_', ' ')
