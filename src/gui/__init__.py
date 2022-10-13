from threading import Thread
from src.gui.gui import GUI

consumer = Thread(target=GUI.run, daemon=True, name="GUI_Daemon")
consumer.start()

def join():
    GUI.add_event(None, None)
    consumer.join()


__all__ = [GUI, join]
