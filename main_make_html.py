from .Make_html import html
from .dlg_config import DlgConfig

def main(path):

    config = DlgConfig()
    config.run()

    Documento = html(path)
    Documento.write_html()
    Documento.copy_labels()
