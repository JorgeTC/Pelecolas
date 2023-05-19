import __init__
from src.essays.google_api import Poster
from src.essays.html import ContentMgr, Html
from src.gui import YesNo


def main():

    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    b_otra = True
    while b_otra:
        # Objeto que escribe el html
        Documento = Html()
        # Genero el html
        Documento.write_html()

        # Leo el html escrito y extraigo los datos necesarios para hacer la publicación
        post_data = ContentMgr.extract_html(Documento.file_name)
        # Le doy al objeto que añade el post al blog todos los datos
        Poster.add_post(title=post_data.title,
                        content=post_data.content,
                        labels=post_data.labels)

        # Pregunto si quiere generar otra reseña
        b_otra = YesNo(question="¿Otra reseña? ", empty_ans=True).get_ans()

        # Elimino el archivo html que acabo de generar
        Documento.delete_file()


if __name__ == "__main__":
    main()
