import __init__
from src.essays.google_api import Poster
from src.essays.html import ContentMgr, Html
from src.gui import YesNo


def main():

    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    while True:
        # Objeto que escribe el html
        try:
            Documento = Html()
        except KeyboardInterrupt:
            break
        # Genero el html
        Documento.write_html()

        # Leo el html escrito y extraigo los datos necesarios para hacer la publicación
        post_data = ContentMgr.extract_html(Documento.file_name)
        # Le doy al objeto que añade el post al blog todos los datos
        Poster.add_post(title=post_data.title,
                        content=post_data.content,
                        labels=post_data.labels)

        # Pregunto si quiere generar otra reseña
        try:
            other = YesNo(question="¿Otra reseña? ", empty_ans=True).get_ans()
        except KeyboardInterrupt:
            other = False

        # Elimino el archivo html que acabo de generar
        Documento.delete_file()

        if not other:
            break


if __name__ == "__main__":
    main()
