import __init__
from src.essays.html import Html
from src.gui import YesNo


def main():

    # Inicializo un bucle para poder crear tantas reseñas como se quiera
    # sin necesidad de cerrar la aplicación
    while True:
        # Objeto que escribe el html
        Documento = Html()
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
