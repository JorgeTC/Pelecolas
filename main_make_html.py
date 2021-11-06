from .Make_html import html
import keyboard

def main(path):

    if keyboard.is_pressed('ctrl'):
        from .dlg_config import DlgConfig
        config = DlgConfig()
        config.run()

    Documento = html(path)
    Documento.write_html()
    Documento.copy_labels()
