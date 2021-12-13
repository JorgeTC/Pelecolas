from src.dlg_config import manage_config

def main(path):

    manage_config()

    from src.make_html import html
    from src.dlg_bool import YesNo
    from src.poster import POSTER
    from src.content_mgr import ContentMgr


    # Objeto que escribe el html
    Documento = html(path)
    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    b_otra = True
    dlg_otra = YesNo(question="¿Otra reseña? ", empty_ans=True)
    while b_otra:
        # Genero el html
        Documento.write_html()

        # Leo el html escrito y extraigo los datos necesarios para hacer la publicación
        mgr = ContentMgr(path)
        post_data = mgr.extract_html(Documento.data.titulo)
        # Le doy al objeto que añade el post al blog todos los datos
        POSTER.add_post(title=post_data['title'],
                  content=post_data['content'],
                  labels=post_data['labels'])

        # Pregunto si quiere generar otra reseña
        b_otra = dlg_otra.get_ans()

        # Elimino el archivo html que acabo de generar
        Documento.delete_file()
        # Limpio el objeto para poder escribir otro html
        Documento.reset()

