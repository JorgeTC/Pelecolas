import re
import urllib.parse
from dataclasses import dataclass

import textacy
from spacy.tokens.span import Span

from src.aux_console import clear_current_line, delete_line, go_to_upper_row
from src.aux_res_directory import get_res_folder
from src.blog_csv_mgr import CSV_COLUMN, BlogCsvMgr
from src.blog_scraper import BlogScraper
from src.config import Config, Param, Section
from src.dlg_bool import YesNo


@dataclass
class DirectorCitation():
    position: int
    director: str
    length: int


@dataclass
class FilmCitation():
    begin: int
    end: int
    title: str


class Quoter(BlogCsvMgr):
    INI_QUOTE_CHAR = "“"
    FIN_QUOTE_CHAR = "”"

    OPEN_LINK = "<a href=\"{}\">"
    CLOSE_LINK = "</a>"
    LINK_LABEL = "https://pelecolas.blogspot.com/search/label/{}"

    def __init__(self) -> None:
        # Necesito el csv, así que lo escribo
        if self.is_needed():
            BlogScraper().write_csv()

        # Guardo las citaciones que vaya sugiriendo
        self.__quoted_directors: set[str] = set()
        self.__titles: set[str] = set()
        self.__personajes: set[str] = set()

        # Texto que estoy estudiando actualmente
        self.__ori_text = ""
        # Película actual.
        # No quiero citarme a mi mismo
        self.titulo = ""
        # Director actual, no quiero citarle
        self.director = ""

        # Lector de csv
        self.__csv_reader = self.open_to_read()

        # Cuántas preguntas he hecho para la película actual
        self.questions_counter = 0

        # Procesador de lenguaje para obtener nombres propios
        # Cargando el modelo en español de spacy
        self.__nlp = textacy.load_spacy_lang('es_core_news_sm')
        self.__all_director = self.__get_directors_indexed()

        # Lista de apellidos que siempre que aparezcan se referirán al director
        self.__trust_directors = load_trust_directors()

    def quote_parr(self, text: str) -> str:
        # Guardo el párrafo recién introducido
        self.__ori_text = text

        self.__quote_titles()
        self.__quote_directors()
        return self.__ori_text

    def __quote_titles(self) -> None:
        # Cuento cuántas comillas hay
        ini_comillas_pos = find(self.__ori_text, self.INI_QUOTE_CHAR)
        fin_comillas_pos = find(self.__ori_text, self.FIN_QUOTE_CHAR)
        if len(ini_comillas_pos) != len(fin_comillas_pos):
            assert("Comillas impares, no se citará este párrafo")
            return

        # Construyo una lista con todas las posibles citas
        posible_titles = [FilmCitation(begin=i,
                                       end=j,
                                       title=self.__ori_text[i + 1:j])
                          for i, j in zip(ini_comillas_pos, fin_comillas_pos)]

        while posible_titles:
            title = posible_titles.pop()
            row = self.__row_in_csv(title.title)
            # La película no está indexada
            if row < 0:
                continue
            # Si la película ya está citada, no la cito otra vez
            if title.title in self.__titles:
                continue
            # Si la cita es la película actual, no añado link
            if title.title == self.titulo:
                continue
            # Guardo este título como ya citado
            self.__titles.add(title.title)
            self.__add_post_link(title, row)

    def __add_post_link(self, citation: FilmCitation, row: int) -> None:
        # Construyo el html para el enlace
        ini_link = self.OPEN_LINK.format(
            self.__csv_reader[row][int(CSV_COLUMN.LINK)])

        # Escribo el cierre del link
        position = citation.end
        self.__ori_text = insert_string_in_position(
            self.__ori_text, self.CLOSE_LINK, position)

        # Escribo el inicio del link
        position = citation.begin + 1
        self.__ori_text = insert_string_in_position(
            self.__ori_text, ini_link, position)

    def __quote_directors(self) -> None:
        # Con procesamiento de lenguaje extraigo lo que puede ser un nombre
        nombres = self.extract_names(self.__ori_text)
        # Inicio una lista para buscar apariciones de los directores en el texto
        ini_director_pos: list[DirectorCitation] = []
        # Compruebo que el nombre corresponda con un director indexado
        for nombre in nombres:
            # Si ya he preguntado por este nombre paso al siguiente
            if nombre in self.__personajes:
                continue
            # Lo guardo como nombre ya preguntado
            self.__personajes.add(nombre)
            for director in self.__all_director:
                # No quiero citar dos veces el mismo director
                if director in self.__quoted_directors:
                    continue
                # No quiero citar al director actual
                if director == self.director:
                    continue
                # Puede que sólo esté escrito el apellido del director
                if not self.__is_name_in_director(nombre, director):
                    continue
                # Pido confirmación al usuario de la cita
                if not self.__ask_confirmation(nombre, director):
                    continue
                citation = DirectorCitation(position=self.__ori_text.find(nombre),
                                            director=director,
                                            length=len(nombre))
                ini_director_pos.append(citation)
                # Lo guardo como director ya citado
                self.__quoted_directors.add(director)
                break

        # Ahora ya tengo los índices que quería
        while ini_director_pos:
            self.__add_director_link(ini_director_pos.pop())

    def __is_name_in_director(self, name: str, director: str) -> bool:
        patron = r'\b({0})\b'.format(name)
        return bool(re.search(patron, director))

    def __ask_confirmation(self, nombre: str, director: str) -> bool:
        # Si son idénticos, evidentemente es una cita
        if nombre == director:
            return True
        # Si es una referencia que siempre se ejecuta igual, es una cita
        if nombre in self.__trust_directors:
            return True
        # En caso contrario, pregunto
        self.questions_counter += 1
        clear_current_line()
        pregunta = "¿Es {} una cita de {}? ".format(nombre, director)
        question = YesNo(pregunta)
        ans = question.get_ans()
        return bool(ans)

    def __add_director_link(self, cit: DirectorCitation) -> None:
        # Escribo el cierre del hipervínculo
        self.__ori_text = insert_string_in_position(
            self.__ori_text, self.CLOSE_LINK, cit.position + cit.length)

        # Construyo el link
        dir = urllib.parse.quote(cit.director)
        link = self.LINK_LABEL.format(dir)
        # Construyo el html para el enlace
        ini_link = self.OPEN_LINK.format(link)
        # Escribo el inicio del hipervínculo
        self.__ori_text = insert_string_in_position(
            self.__ori_text, ini_link, cit.position)

    def __row_in_csv(self, title: str) -> int:
        for index, row in enumerate(self.__csv_reader):
            if title.lower() == row[int(CSV_COLUMN.TITLE)].lower().strip("\""):
                return index

        # No lo hemos encontrado
        return -1

    def extract_names(self, text: str) -> list[str]:
        # Usando un procesador de lenguaje natural extraigo los nombres del párrafo
        texto_procesado = self.__nlp(text)

        personajes = []
        for ent in texto_procesado.ents:
            # Sólo lo añado a mi lista si la etiqueta asignada dice personaje
            if self.__is_person(ent):
                if ent.lemma_ not in personajes:
                    personajes.append(str(ent.lemma_))

        return personajes

    def __is_person(self, ent: Span) -> bool:
        # Aplico un correctivo a los Coen
        if (ent.lemma_ == 'Coen'):
            return True

        # Elimino los pronombres
        if (ent.lemma_ == 'yo' or ent.lemma_ == 'él'):
            return False

        # Caso general en el que me fio del modelo
        return ent.label_ == 'PER'

    def __get_directors_indexed(self) -> set[str]:
        # Listamos los directores que hay en el csv asegurando una única ocurrencia de ellos
        return {row[int(CSV_COLUMN.DIRECTOR)] for row in self.__csv_reader}

    def clear_questions(self) -> None:
        # Elimino todas las preguntas por directores
        for _ in range(self.questions_counter):
            go_to_upper_row()
            delete_line()
            print("")

    def reset(self) -> None:
        # Dejo el objeto listo para usar de nuevo
        # Elimino todos los datos relativos a la última reseña
        self.titulo = ""
        self.director = ""
        # Borro las preguntas del director
        self.clear_questions()
        self.questions_counter = 0
        # Limpio las listas de las citaciones ya realizadas
        self.__quoted_directors.clear()
        self.__titles.clear()
        self.__personajes.clear()


def load_trust_directors() -> set[str]:
    # Leo si el ini me pide nuevos directores
    new_directors = Config.get_value(Section.HTML, Param.YES_ALWAYS_DIR)
    new_directors = new_directors.split(",")
    # Elimino espacios innecesarios
    new_directors = [director.strip() for director in new_directors]
    # Evito guardar cadenas vacías
    new_directors = [director for director in new_directors if director]

    # Creo el conjunto de directores
    directors = set(new_directors)

    # Cargo los directores del archivo
    path = get_res_folder("Make_html", "Trust_directors.txt")
    if path.is_file():
        directors.update(open(path, encoding="utf-8").read().splitlines())

    # Guardo de nuevo el archivo
    with open(path, 'w', encoding="utf-8") as f:
        f.write("\n".join(directors))

    # Ya los he añadido, los puedo borrar del ini
    Config.set_value(Section.HTML, Param.YES_ALWAYS_DIR, "")

    # Devuelvo el conjunto
    return directors


def find(s: str, ch: str) -> list[int]:
    return [i for i, ltr in enumerate(s) if ltr == ch]


def insert_string_in_position(sr: str, sub: str, pos: int) -> str:
    return sr[:pos] + sub + sr[pos:]
