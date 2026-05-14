import __init__
from src.essays.html import Html, ask_for_data
from src.gui import YesNo


def main():

    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    while True:
        try:
            # Pido los datos de la película
            film_data = ask_for_data()
        except KeyboardInterrupt:
            break

        # Objeto que escribe el html
        Documento = Html(film_data)
        # Genero el html
        Documento.write_html()

        # Pregunto si quiere generar otra reseña
        try:
            other = YesNo(question="¿Otra reseña? ", empty_ans=True).get_ans()
        except KeyboardInterrupt:
            other = False
        if not other:
            break


if __name__ == "__main__":
    main()
