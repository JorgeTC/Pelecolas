from threading import Thread

from .api_dataclasses import Blog, DriveFile, Post
from .google_client import GoogleClient
from .google_drive import Drive
from .poster import Poster

# Inicializo el ejecutor de tareas de la api de Google
consumer = Thread(target=GoogleClient.run_queue, daemon=True, name="Google_Daemon")
consumer.start()

def join():
    GoogleClient.close_queue()
    consumer.join()

__all__ = [Poster, Drive,
           Post, DriveFile, Blog,
           join]
