import cloudscraper
import requests

# Hemos separado esta función en un solo archivo para asegurarnos
# de que no se realiza ningún request directamente en ningún otro sitio del código.
# Cuando se hagan peticiones de url se deberían hacer con este sistema de seguridad.

# Objeto necesario para realizar requests a páginas protegidas por Cloudflare
scraper = cloudscraper.create_scraper(
    # Si no explicito que quiero la versión desktop,
    # cloudscraper puede elegir cualquiera de las dos imprevisiblemente.
    # Incluso si la url incluye "m." devolverá la versión desktop.
    # El atributo "platform" hay que proveerlo porque si no, falla la inicialización.
    browser = {"platform": "linux", "desktop": True, "mobile": False},
)


def safe_response(url: str) -> requests.Response:
    # Repite el request hasta que se pueda completar sin error
    while True:
        try:
            return scraper.get(url)
        except Exception:
            continue
