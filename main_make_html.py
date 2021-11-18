from dlg_config import manage_config

def main(path):

    manage_config()

    from Make_html import html
    from dlg_bool import YesNo

    Documento = html(path)
    b_otra = True
    dlg_otra = YesNo(question="¿Otra reseña?")
    while b_otra:
        Documento.write_html()
        Documento.copy_labels()

        b_otra = dlg_otra.get_ans()
        if b_otra:
            Documento.reset()
