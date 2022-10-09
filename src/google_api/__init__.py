from threading import Thread
from src.google_api.google_client import GoogleClient
from src.google_api.google_drive import Drive
from src.google_api.poster import Poster

# Inicializo el ejecutor de tareas de la api de Google
consumer = Thread(target=GoogleClient.run_queue, daemon=True)
consumer.start()

__all__ = [Poster, Drive]
