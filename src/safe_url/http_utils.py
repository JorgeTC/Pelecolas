import cloudscraper
import requests

# Hemos separado esta función en un solo archivo para asegurarnos
# de que no se realiza ningún request directamente en ningún otro sitio del código.
# Cuando se hagan peticiones de url se deberían hacer con este sistema de seguridad.

# Objeto necesario para realizar requests a páginas protegidas por Cloudflare
scraper = cloudscraper.create_scraper()

def safe_response(url: str) -> requests.Response:
    # Repite el request hasta que se pueda completar sin error
    while True:
        try:
            return scraper.get(url)
        except Exception:
            continue
