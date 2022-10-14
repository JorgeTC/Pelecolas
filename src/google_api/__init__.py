from threading import Thread

from src.google_api.api_dataclasses import Blog, DriveFile, Post
from src.google_api.google_client import GoogleClient
from src.google_api.google_drive import Drive
from src.google_api.poster import Poster

# Inicializo el ejecutor de tareas de la api de Google
consumer = Thread(target=GoogleClient.run_queue, daemon=True, name="Google_Daemon")
consumer.start()

def join():
    GoogleClient.REQUESTS_QUEUE.put(None)
    consumer.join()

__all__ = [Poster, Drive,
           Post, DriveFile, Blog,
           join]
