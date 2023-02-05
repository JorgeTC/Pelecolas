from threading import Thread

from .dlg_bool import YesNo
from .dlg_scroll_base import DlgScrollBase
from .gui import GUI
from .input import Input
from .log import Log
from .progress_bar import ProgressBar

consumer = Thread(target=GUI.run, daemon=True, name="GUI_Daemon")
consumer.start()


def join_GUI():
    GUI.close_gui()
    consumer.join()


__all__ = [GUI, join_GUI, Log, Input, DlgScrollBase, ProgressBar, YesNo]
