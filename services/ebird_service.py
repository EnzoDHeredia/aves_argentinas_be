
import os
from dotenv import load_dotenv
import requests
from config import logger

class EBirdService:
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.environ.get("EBIRD_API_KEY", "")
        self.base_url = "https://api.ebird.org/v2"
        self.region_code = "AR"  # Argentina fijo
        
    def get_recent_observations(self, species_code, max_results=10):
        """Obtener observaciones recientes de una especie en Argentina"""
        if not species_code:
            logger.warning("No se proporcionó species_code")
            return []
            
        url = f"{self.base_url}/data/obs/{self.region_code}/recent/{species_code}"
        headers = {
            "X-eBirdApiToken": self.api_key
        }
        
        params = {
            "maxResults": max_results,
            "includeProvisional": True
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Obtenidas {len(data)} observaciones para {species_code}")
                
                # Formatear datos para el frontend
                formatted_observations = []
                for obs in data:
                    formatted_obs = {
                        "locName": obs.get("locName", "Ubicación desconocida"),
                        "obsDt": obs.get("obsDt", ""),
                        "howMany": obs.get("howMany", 1),
                        "lat": obs.get("lat"),
                        "lng": obs.get("lng"),
                        "locId": obs.get("locId", ""),
                        "obsValid": obs.get("obsValid", True),
                        "obsReviewed": obs.get("obsReviewed", False)
                    }
                    
                    # Solo incluir observaciones con coordenadas válidas
                    if formatted_obs["lat"] is not None and formatted_obs["lng"] is not None:
                        formatted_observations.append(formatted_obs)
                
                return formatted_observations[:max_results]
                
            elif response.status_code == 404:
                logger.info(f"No se encontraron observaciones para {species_code} en {self.region_code}")
                return []
            else:
                logger.error(f"Error en eBird API: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al consultar eBird para {species_code}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con eBird: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado en eBird Service: {e}")
            return []
