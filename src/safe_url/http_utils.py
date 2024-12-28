import requests

# Hemos separado esta función en un solo archivo para asegurarnos
# de que no se realiza ningún request directamente en ningún otro sitio del código.
# Cuando se hagan peticiones de url se deberían hacer con este sistema de seguridad.

def safe_response(url: str) -> requests.Response:
    # Repite el request hasta que se pueda completar sin error
    while True:
        try:
            return requests.get(url)
        except Exception:
            continue
