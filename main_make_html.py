from .dlg_config import manage_config

def main(path):

    manage_config()

    from .Make_html import html
    Documento = html(path)
    Documento.write_html()
    Documento.copy_labels()
