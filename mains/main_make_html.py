import __init__
from src.gui import YesNo
from src.html import html


def main():

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


if __name__ == "__main__":
    main()
