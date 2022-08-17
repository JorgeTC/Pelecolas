import docx
from docx.text.paragraph import Paragraph

from src.config import Config, Section, Param
from src.word_folder_mgr import WordFolderMgr

SEPARATOR_YEAR = " - "


def get_bold_title(paragraph: Paragraph) -> str:
    # Obtengo el primer fragamento de texto que esté en negrita.
    titulo = ""

    for run in paragraph.runs:
        # Conservo las negritas
        if not run.bold:
            # he llegado al final del título
            break
        titulo += run.text

    return titulo


def get_title(paragraph: Paragraph) -> str:

    # Obtengo lo que esté en negrita
    title = get_bold_title(paragraph)

    # Compruebo que lo que he leído sea un título.
    # Busco que su separador sean dos puntos.
    # Elimino los espacios que fueren delante del separador.
    title = title.strip(" ")
    # Compruebo que esté presente el separador.
    if not title or title[-1] != ":":
        title = ""
    else:
        # Ya he usado los dos puntos para reconocer el título.
        # Ahora los puedo eliminar para tener limpio el título.
        title = title.strip(": ")

    return title


def is_break_line(text: str) -> bool:

    # Limpio de espacios el texto
    text = text.strip()

    # Compruebo que contenga un salto de linea
    if text in ('', "\t", "\n"):
        return True

    # Es un párrafo y no un salto de línea
    return False


class WordReader(WordFolderMgr):
    # Me quedo con el nombre del archivo sin la extensión.
    HEADER = str(WordFolderMgr.SZ_ALL_DOCX[0].stem).split(SEPARATOR_YEAR)[0]
    # Me guardo sólo los párrafos, es lo que voy a iterar más adelante
    PARAGRAPHS: list[Paragraph] = []
    # Guardo a qué párrafo corresponde cada año
    YEARS_PARR: dict[str, int] = {}
    # Lista con todos los títulos que encuentre.
    TITULOS: dict[str, int] = {}

    @classmethod
    def __has_next_parr_title(cls, text: str) -> bool:
        if cls.__is_header(text):
            # No cuento el encabezado del documento
            return False
        if is_break_line(text):
            # Si hay un doble salto de párrafo, quizás ha terminado una crítica
            # El inicio del siguiente párrafo será el título de la película
            return True

        return False

    @staticmethod
    def is_break_line(text: str) -> bool:

        # Limpio de espacios el texto
        text = text.strip()

        # Compruebo que contenga un salto de linea
        if text in ('', "\t", "\n"):
            return True

        # Es un párrafo y no un salto de línea
        return False

    @classmethod
    def __is_header(cls, text: str) -> bool:
        # Quiero que el código valga para contar las películas y los libros.
        # No sé qué encabezado me voy a encontrar en mi documento.
        return text == cls.HEADER

    @classmethod
    def __append_title(cls, paragraph: Paragraph, index: int) -> bool:
        # Leo el posible título de este párrafo.
        titulo = get_title(paragraph)
        # Si no se ha encontrado título, no es el inicio de una crítica.
        if not titulo:
            # No he conseguido añadir nada.
            return False

        if titulo not in cls.TITULOS:
            # En este punto ya sabemos que tenemos un título
            cls.TITULOS[titulo] = index
        else:
            # Si el título ya está recogido, aviso al usuario de que está mal escrito el Word
            print(f"Repeated title {titulo}")

        # He añadido un título.
        return True

    @classmethod
    def init_titles(cls) -> None:
        # inicializo la variable.
        # No quiero buscar desde el principio porque sé que encontraré el título del documento.
        search_title = False

        # Recorro todos los párrafos del documento
        for i, paragraph in enumerate(cls.PARAGRAPHS):
            if not search_title:
                # Compruebo si el próximo párrafo podría tener un título.
                search_title = cls.__has_next_parr_title(paragraph.text)
            else:
                # Probablemente estoy en un párrafo que es el primero de una crítica.
                # Si he añadido un título, no me espero que el siguiente párrafo comience con título.
                # Si no he añadido nada, sigo buscando.
                search_title = not cls.__append_title(paragraph, i)

    @classmethod
    def list_titles(self) -> list[str]:
        return list(self.TITULOS.keys())

    @classmethod
    def write_list(cls) -> None:
        output_path = Config.get_folder_path(
            Section.COUNT_FILMS, Param.TITLE_LIST_PATH)
        # Abro el documento txt para escribirlo
        titulos_doc = open(output_path / "Titulos de reseñas.txt", "w",
                           encoding='utf-8')

        # Miro si hay que escribir el índice
        b_index = Config.get_bool(Section.COUNT_FILMS, Param.ADD_INDEX)

        # Miro si hay que escribir el año
        b_year = Config.get_bool(Section.COUNT_FILMS, Param.ADD_YEAR)
        next_years = iter(cls.YEARS_PARR.keys())
        # Cojo el primero de los años que hay que iterar
        next_year = next(next_years, None)

        for index, titulo in enumerate(cls.TITULOS):

            # Escritura del año
            if b_year:
                # Compruebo que el título actual esté en una posición superior a donde inicia el siguiente año.
                # No me espero el caso de igualdad ya que ese párrafo corresponde al título del Word: peliculas.
                if cls.TITULOS[titulo] > cls.YEARS_PARR[next_year]:
                    # Escribo el año en el documento
                    titulos_doc.write("***" + str(next_year) + "***\n")
                    # Avanzo al siguiente año
                    past_year = next_year
                    next_year = next(next_years, past_year)
                    # Si es el último año, dejo de escribir años
                    if next_year == past_year:
                        b_year = False

            # Si tengo que añadir el índice cojo el número y añado un espacio
            if b_index:
                titulos_doc.write(str(index + 1) + " " + titulo + "\n")
            else:
                titulos_doc.write(titulo + "\n")

        # cierro el documento
        titulos_doc.close()

    @classmethod
    def init_paragraphs(cls) -> None:
        # Itero todos los docx que he encontrado
        for word in WordFolderMgr.SZ_ALL_DOCX:
            # Obtengo el año actual
            try:
                year = word.stem.split(SEPARATOR_YEAR)[1]
            except IndexError:
                year = "2017"
            # Guardo en qué párrafo empieza el año actual
            cls.YEARS_PARR[year] = len(cls.PARAGRAPHS)
            # Añado los párrafos del docx actual
            # Evito añadir el primero, donde está el título del documento
            try:
                cls.PARAGRAPHS = cls.PARAGRAPHS + \
                    docx.Document(word).paragraphs[1:]
            except:
                pass

WordReader.init_paragraphs()
WordReader.init_titles()
