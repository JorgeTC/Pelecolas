import logging
import urllib.parse
from typing import Iterable, NamedTuple

from src.aux_res_directory import get_res_folder
from src.config import Config, Param, Section
from src.gui import YesNo

from ...async_initializer import AsyncInitializer
from .quoter_base import QuoterBase, insert_string_in_position


class DirectorCitation(NamedTuple):
    position: int
    director: str
    length: int


def load_new_directors() -> set[str]:
    # Leo si el ini me pide nuevos directores
    new_directors_config = Config.get_value(Section.HTML, Param.YES_ALWAYS_DIR)
    new_directors = new_directors_config.split(",")
    # Elimino espacios innecesarios
    new_directors = [director.strip() for director in new_directors]
    # Evito guardar cadenas vacías
    new_directors = [director for director in new_directors if director]

    if new_directors:
        logging.debug(f"New directors to always quote loaded from config: {", ".join(new_directors)}")

    # Devuelvo el conjunto de nuevos directores
    return set(new_directors)

def load_trust_directors() -> set[str]:
    # Creo el conjunto de directores
    directors = load_new_directors()

    # Cargo los directores del archivo
    path = get_res_folder("Make_html", "Trust_directors.txt")
    if path.is_file():
        logging.debug(f"Loading trusted directors from {path}")
        with open(path, encoding="utf-8") as file_directors:
            directors.update(file_directors.read().splitlines())

    # Guardo de nuevo el archivo
    with open(path, 'w', encoding="utf-8") as f:
        f.write("\n".join(directors))

    # Ya los he añadido, los puedo borrar del ini
    Config.set_value(Section.HTML, Param.YES_ALWAYS_DIR, "")

    # Devuelvo el conjunto
    return directors


def init_all_directors():
    csv_rows = QuoterBase.csv_content.get()
    return {row.director for row in csv_rows}


class QuoterDirector:

    # Registro de todos los directores reseñados
    ALL_DIRECTORS = AsyncInitializer(init_all_directors)

    # Lista de apellidos que siempre que aparezcan se referirán al director
    TRUST_DIRECTORS = load_trust_directors()

    def __init__(self, director: str):

        # Director actual, no quiero citarle
        self.director = director

        # Guardo las citaciones que vaya sugiriendo
        self._quoted_directors: set[str] = set()
        self._personajes: set[str] = set()

    def quote_directors(self, text: str) -> str:
        # Inicio una lista para buscar apariciones de los directores en el texto
        ini_director_pos: list[DirectorCitation] = []

        # Recorro las palabras buscando que sea el apellido de un director
        for position, word in split_words(text):
            if citation := self.__quote_word(text, position, word):
                ini_director_pos.append(citation)

        # Ahora ya tengo los índices que quería
        while ini_director_pos:
            text = add_director_link(text, ini_director_pos.pop())

        return text

    def __quote_word(self, text: str, it_position: int, it_word: str) -> DirectorCitation | None:

        # Inicializo una lista con los personajes que se vayan a preguntar
        personajes_preguntados: set[str] = set()

        # Variable de retorno
        citation: DirectorCitation | None = None

        # Recorro todos los directores buscando la palabra que tengo
        for director in self.ALL_DIRECTORS.get():
            # No quiero citar dos veces el mismo director
            if director in self._quoted_directors:
                continue
            # No quiero citar al director actual
            if director == self.director:
                continue
            position, word = complete_quote(text,
                                            it_position, it_word,
                                            director)
            if not word:
                continue
            logging.debug(f"Possible director quote found: '{word}' for director '{director}'")
            # Si ya he preguntado por este nombre paso al siguiente
            if word in self._personajes:
                continue
            personajes_preguntados.add(word)
            # Pido confirmación al usuario de la cita
            if not self.__ask_confirmation(word, director):
                continue
            citation = DirectorCitation(position=position,
                                        director=director,
                                        length=len(word))
            # Lo guardo como director ya citado
            self._quoted_directors.add(director)
            break

        # Actualizo el conjunto de nombres ya preguntados
        self._personajes.update(personajes_preguntados)

        # Devuelvo la posible citación
        return citation

    def __ask_confirmation(self, nombre: str, director: str) -> bool:
        # Si son idénticos, evidentemente es una cita
        if nombre == director:
            return True
        # Si es una referencia que siempre se ejecuta igual, es una cita
        if nombre in self.TRUST_DIRECTORS:
            return True
        # En caso contrario, pregunto
        pregunta = f"¿Es {nombre} una cita de {director}? "
        return YesNo(pregunta).get_ans()


def split_words(text: str) -> Iterable[tuple[int, str]]:
    # Inicializo las variables de retorno
    new_word = ""
    index_begin_word = 0

    # Aún no he visto ningunas comillas que me digan que estoy en un título
    in_title = False
    # Aún no he visto que esté entre comillas
    in_italic = False
    # Aún no he visto que esté en un link
    in_link = False

    # Recorro los caracteres
    for index, char in enumerate(text):

        # Proceso las letras
        if char.isalpha() and not in_title and not in_italic and not in_link:

            # Comienza una palabra, me guardo la posición actual
            if not new_word:
                index_begin_word = index

            # Aumento la palabra actual
            new_word = new_word + char
        else:
            # No es una letra, no añado los caracteres
            if new_word:
                yield index_begin_word, new_word
                new_word = ""

            # Empieza el título de una película, no puede haber directores ahí dentro
            if char == QuoterBase.INI_QUOTE_CHAR:
                in_title = True
            elif char == QuoterBase.FIN_QUOTE_CHAR:
                in_title = False

            # Empieza una cursiva
            if begins_italic(index, text):
                in_italic = True
            elif ends_italic(index, text):
                in_italic = False

            # Empieza un link
            if begins_link(index, text):
                in_link = True
            elif ends_link(index, text):
                in_link = False

    if not in_title and not in_link and not in_italic:
        yield index_begin_word, new_word


def begins_link(index: int, text: str) -> bool:
    return begins_tag(index, text, "<a href")


def ends_link(index: int, text: str) -> bool:
    return ends_tag(index, text, "</a>")


def begins_italic(index: int, text: str) -> bool:
    return begins_tag(index, text, "<i>")


def ends_italic(index: int, text: str) -> bool:
    return ends_tag(index, text, "</i>")


def begins_tag(index: int, text: str, tag: str) -> bool:
    # Debe empezar con el símbolo correspondiente
    if text[index] != tag[0]:
        return False

    # Debe caber el tag de html
    if index + len(tag) >= len(text):
        return False

    # Devuelvo si es el inicio de una cursiva
    return text[index: index + len(tag)] == tag


def ends_tag(index: int, text: str, tag: str) -> bool:
    # Debe acabar con el símbolo correspondiente
    if text[index] != tag[-1]:
        return False

    # Debe caber el tag de html
    if index + 1 - len(tag) < 0:
        return False

    # Devuelvo si es el fin de una cursiva
    return text[index + 1 - len(tag): index + 1] == tag


def reverse_iterate_director(director: str) -> Iterable[str]:
    # Itero el nombre del director al revés.
    # Dividiré las palabras de la misma forma que estoy dividiendo el texto.
    for chars_till_end, reverse_word in split_words(director[::-1]):
        # Añado una palabra más
        yield director[-chars_till_end-len(reverse_word):]


def complete_quote(text: str, index: int, word: str, director: str) -> tuple[int, str]:

    # Posición del texto en la que debe acabar la cita
    INDEX_END_QUOTE = index + len(word)

    # Trozo de texto que sabemos seguro que es cita
    whole_quote = ""
    # Inicio de cita
    index_begin_quote = INDEX_END_QUOTE

    for surname in reverse_iterate_director(director):
        # Compruebo que la cita coincida
        lower_index = min(INDEX_END_QUOTE - len(surname), index)
        longest_quote = text[lower_index:INDEX_END_QUOTE]
        if not equals(longest_quote, surname):
            break

        # Para que sea una cita, la primera letra debe ser mayúscula
        if longest_quote[0] != longest_quote[0].lower():
            # Si todo va bien, actualizo los valores de respuesta
            index_begin_quote = lower_index
            whole_quote = longest_quote

    return index_begin_quote, whole_quote


def equals(text: str, surname: str) -> bool:
    if not text:
        return False
    if text == surname:
        return True

    # Caso en el que el apellido haya adquirido mayúsculas por la puntuación
    text = text[0].lower() + text[1:]
    return text == surname


def add_director_link(text: str, cit: DirectorCitation) -> str:
    # Escribo el cierre del hipervínculo
    text = insert_string_in_position(text, QuoterBase.CLOSE_LINK,
                                     cit.position + cit.length)

    # Construyo el link
    dir = urllib.parse.quote(cit.director)
    link = QuoterBase.LINK_LABEL(dir)
    # Construyo el html para el enlace
    ini_link = QuoterBase.OPEN_LINK(link)
    # Escribo el inicio del hipervínculo
    text = insert_string_in_position(text, ini_link,
                                     cit.position)

    return text
