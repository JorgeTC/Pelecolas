import docx
import os

def get_title(paragraph):
    # Dado un texto, extraigo toda la primera negrita
    titulo = ""

    for run in paragraph.runs:
        # Conservo las negritas
        if not run.bold:
            # he llegado al final del título
            break
        titulo += run.text

    return titulo

def is_break_line(text):
    if text == '':
        return True
    if text == "\t":
        return True
    if text == "\n":
        return True

    return False


def get_word_file_name():
    # Me espero un único archivo docx
    all_files = os.listdir()
    all_files = [x for x in all_files if x.endswith(".docx")]

    return all_files[0]

def write_list(titulos):
    titulos_doc = open("Titulos de reseñas.txt", "w")

    for titulo in titulos:
        titulos_doc.write(titulo + "\n")

    # cierro el documento
    titulos_doc.close()


if __name__ == "__main__":
    # Abro el documento para leerlo
    sz_literatura = get_word_file_name()
    doc = docx.Document(sz_literatura)

    # inicializo las variables
    search_title = False
    titulos = []

    # Recorro todos los párrafos del documento
    for paragraph in doc.paragraphs:
        if not search_title:
            if paragraph.text == 'Literatura':
                # No cuento el encabezado del documento
                continue
            if is_break_line(paragraph.text):
                # Si hay un doble salto de párrafo, quizás ha terminado una crítica
                # El inicio del siguiente párrafo será el título de la película
                search_title = True
        else:
            # Sé que estoy en un párrafo que es el primero de una crítica
            # Este párrafo comenzará con el título de la película
            # El título se separa de la crítica con dos puntos
            titulo = get_title(paragraph)
            # Si no se ha encontrado nada en negrita, no hay un título
            if not titulo:
                continue

            # Compruebo que el último caracter sea :
            titulo = titulo.strip(" ")
            if titulo[-1] != ":":
                continue

            # En este punto ya sabemos que tenemos un titulo
            titulo = titulo.strip(":")
            titulos.append(titulo)

            # Devuelvo la variable a su valor original
            search_title = False

    write_list(titulos)

    print(len(titulos))
    input("Press Enter to continue...")
