from src.config import manage_config


def main():

    manage_config()

    from src.dlg_bool import YesNo
    from src.make_html import html

    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    b_otra = True
    while b_otra:
        # Objeto que escribe el html
        Documento = html()
        # Genero el html
        Documento.write_html()

        # Pregunto si quiere generar otra reseña
        b_otra = YesNo(question="¿Otra reseña? ", empty_ans=True).get_ans()
