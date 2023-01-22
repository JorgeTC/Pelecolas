import __init__
from src.google_api import Poster
from src.gui import YesNo
from src.html import ContentMgr, html


def main():

    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    b_otra = True
    while b_otra:
        # Objeto que escribe el html
        Documento = html()
        # Genero el html
        Documento.write_html()

        # Leo el html escrito y extraigo los datos necesarios para hacer la publicación
        post_data = ContentMgr.extract_html(Documento.sz_file_name)
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
