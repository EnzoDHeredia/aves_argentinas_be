import requests

# Reemplazá esto por tu API key personal de eBird
EBIRD_API_KEY = "gb7uk3cug8e8"
BASE_URL = "https://api.ebird.org/v2"

# Código de especie (por ejemplo, para "Rupornis magnirostris" es 'rufhor1')
species_code = "rufhor2"
region_code = "AR"  # Código para Argentina

def get_recent_observations(species_code, region_code):
    url = f"{BASE_URL}/data/obs/{region_code}/recent/{species_code}"
    headers = {
        "X-eBirdApiToken": EBIRD_API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"Observaciones recientes de {species_code} en {region_code}:")
        for obs in data[:5]:  # Mostrar solo las primeras 5 para no llenar la consola
            print(f"• {obs['locName']} - {obs['obsDt']} - {obs['howMany'] or '1'} individuo(s)")
    else:
        print("Error:", response.status_code, response.text)

# Ejecutar
get_recent_observations(species_code, region_code)
