import re
import urllib.parse
from dataclasses import dataclass

import textacy
from spacy.tokens.span import Span

from src.aux_console import clear_current_line, delete_line, go_to_upper_row
from src.aux_res_directory import get_res_folder
from src.blog_csv_mgr import CSV_COLUMN
from src.config import Config, Param, Section
from src.dlg_bool import YesNo
from src.quoter_base import QuoterBase, insert_string_in_position


@dataclass
class DirectorCitation():
    position: int
    director: str
    length: int


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


class QuoterDirector:

    # Procesador de lenguaje para obtener nombres propios
    # Cargando el modelo en español de spacy
    NLP = textacy.load_spacy_lang('es_core_news_sm')

    # Registro de todos los directores reseñados
    ALL_DIRECTORS = {row[CSV_COLUMN.DIRECTOR]
                     for row in QuoterBase.CSV_CONTENT}

    # Lista de apellidos que siempre que aparezcan se referirán al director
    TRUST_DIRECTORS = load_trust_directors()

    def __init__(self, director: str):

        # Director actual, no quiero citarle
        self.director = director

        # Guardo las citaciones que vaya sugiriendo
        self.__quoted_directors: set[str] = set()
        self.__personajes: set[str] = set()

        # Cuántas preguntas he hecho para la película actual
        self.questions_counter = 0

    def __is_name_in_director(self, name: str, director: str) -> bool:
        patron = rf'\b({name})\b'
        return bool(re.search(patron, director))

    def quote_directors(self, text: str) -> str:
        # Con procesamiento de lenguaje extraigo lo que puede ser un nombre
        nombres = self.extract_names(text)
        # Inicio una lista para buscar apariciones de los directores en el texto
        ini_director_pos: list[DirectorCitation] = []
        # Compruebo que el nombre corresponda con un director indexado
        for nombre in nombres:
            # Si ya he preguntado por este nombre paso al siguiente
            if nombre in self.__personajes:
                continue
            # Lo guardo como nombre ya preguntado
            self.__personajes.add(nombre)
            for director in self.ALL_DIRECTORS:
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
                citation = DirectorCitation(position=text.find(nombre),
                                            director=director,
                                            length=len(nombre))
                ini_director_pos.append(citation)
                # Lo guardo como director ya citado
                self.__quoted_directors.add(director)
                break

        # Ahora ya tengo los índices que quería
        while ini_director_pos:
            text = add_director_link(text, ini_director_pos.pop())

        return text

    def __ask_confirmation(self, nombre: str, director: str) -> bool:
        # Si son idénticos, evidentemente es una cita
        if nombre == director:
            return True
        # Si es una referencia que siempre se ejecuta igual, es una cita
        if nombre in self.TRUST_DIRECTORS:
            return True
        # En caso contrario, pregunto
        self.questions_counter += 1
        clear_current_line()
        pregunta = f"¿Es {nombre} una cita de {director}? "
        question = YesNo(pregunta)
        ans = question.get_ans()
        return bool(ans)

    def extract_names(self, text: str) -> list[str]:
        # Usando un procesador de lenguaje natural extraigo los nombres del párrafo
        texto_procesado = self.NLP(text)

        personajes = []
        for ent in texto_procesado.ents:
            # Sólo lo añado a mi lista si la etiqueta asignada dice personaje
            if is_person(ent) and ent.lemma_ not in personajes:
                personajes.append(str(ent.lemma_))

        return personajes

    def clear_questions(self) -> None:
        # Elimino todas las preguntas por directores
        for _ in range(self.questions_counter):
            go_to_upper_row()
            delete_line()
            print("")

        # Reseteo el contador
        self.questions_counter = 0


def is_person(ent: Span) -> bool:
    # Aplico un correctivo a los Coen
    if (ent.lemma_ == 'Coen'):
        return True

    # Elimino los pronombres
    if (ent.lemma_ == 'yo' or ent.lemma_ == 'él'):
        return False

    # Caso general en el que me fio del modelo
    return ent.label_ == 'PER'


def add_director_link(text: str, cit: DirectorCitation) -> str:
    # Escribo el cierre del hipervínculo
    text = insert_string_in_position(
        text, QuoterBase.CLOSE_LINK, cit.position + cit.length)

    # Construyo el link
    dir = urllib.parse.quote(cit.director)
    link = QuoterBase.LINK_LABEL(dir)
    # Construyo el html para el enlace
    ini_link = QuoterBase.OPEN_LINK(link)
    # Escribo el inicio del hipervínculo
    text = insert_string_in_position(
        text, ini_link, cit.position)

    return text
