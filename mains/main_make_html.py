from src.dlg_config import manage_config

def main():

    manage_config()

    from src.make_html import html
    from src.dlg_bool import YesNo

    # Objeto que escribe el html
    Documento = html()
    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    b_otra = True
    dlg_otra = YesNo(question="¿Otra reseña? ", empty_ans=True)
    while b_otra:
        # Genero el html
        Documento.write_html()
        Documento.reset()

        # Pregunto si quiere generar otra reseña
        b_otra = dlg_otra.get_ans()

