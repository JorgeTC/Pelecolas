from threading import Thread
from src.gui.gui import GUI

consumer = Thread(target=GUI.run, daemon=True)
consumer.start()

__all__ = [GUI]
