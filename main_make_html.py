from .Make_html import html
from .dlg_config import manage_config

def main(path):

    manage_config()

    Documento = html(path)
    Documento.write_html()
    Documento.copy_labels()
