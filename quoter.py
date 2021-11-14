import textacy
import urllib.parse

from blog_csv_mgr import BlogCsvMgr
from blog_scraper import BlogScraper
from dlg_bool import YesNo


class Quoter(BlogCsvMgr):
    INI_QUOTE_CHAR = "“"
    FIN_QUOTE_CHAR = "”"

    OPEN_LINK = "<a href=\"{}\">"
    CLOSE_LINK = "</a>"
    LINK_LABEL = "https://pelecolas.blogspot.com/search/label/{}"

    def __init__(self) -> None:
        # Necesito el csv, así que lo escribo
        scraper = BlogScraper()
        if self.is_needed():
            scraper.write_csv()

        # Guardo las citaciones que vaya sugeriendo
        self.__directors = []
        self.__titles = []
        self.__personajes = []

        # Texto que estoy estudiando actualmente
        self.__ori_text = ""
        # Película actual.
        # No quiero citarme a mi mismo
        self.titulo = ""
        # Director actual, no quiero citarle
        self.director = ""

        # Lector de csv
        self.__csv_reader = self.open_to_read()

        # Procesador de lenguaje para obtener nombres propios
        # Cargando el modelo en español de spacy
        self.__nlp = textacy.load_spacy_lang('es_core_news_sm')
        self.__get_directors_indexed()

    def quote_parr(self, text):
        # Guardo el párrafo recién introducido
        self.__ori_text = text

        self.__quote_titles()
        self.__quote_directors()
        return self.__ori_text

    def __quote_titles(self):
        # Cuento cuántas comillas hay
        self.__ini_comillas_pos = find(self.__ori_text, self.INI_QUOTE_CHAR)
        self.__fin_comillas_pos = find(self.__ori_text, self.FIN_QUOTE_CHAR)
        if len(self.__ini_comillas_pos) != len(self.__fin_comillas_pos):
            assert("Comillas impares, no se citará este párrafo")
            return

        # Construyo una lista con todas las posibles citas
        posible_titles = []
        for i, j in zip(self.__ini_comillas_pos, self.__fin_comillas_pos):
            posible_titles.append(self.__ori_text[i + 1:j])

        for title in posible_titles:
            row = self.__row_in_csv(title)
            # La película no está indexada
            if row > 0:
                # Si la película ya está citada, no la cito otra vez
                if title not in self.__titles and title != self.titulo:
                    self.__titles.append(title)
                    self.__add_post_link(row)
            # Elimino los índices que ya he usado
            self.__ini_comillas_pos.pop(0)
            self.__fin_comillas_pos.pop(0)

    def __add_post_link(self, row):
        # Construyo el html para el enlace
        ini_link = self.OPEN_LINK.format(self.__csv_reader[row][1])
        # La posición dentro de mi texto me la indica
        # el primer elemento de las listas de índices
        position = self.__ini_comillas_pos[0] + 1
        self.__ori_text = insert_string_in_position(
            self.__ori_text, ini_link, position)
        # Actualizo la posición del cierre de las comillas
        position = self.__fin_comillas_pos[0] + len(ini_link)
        self.__ori_text = insert_string_in_position(
            self.__ori_text, self.CLOSE_LINK, position)

        # Actualizo todo el resto de índices
        delta = len(ini_link) + len(self.CLOSE_LINK)
        self.__ini_comillas_pos = [i + delta for i in self.__ini_comillas_pos]
        self.__fin_comillas_pos = [i + delta for i in self.__fin_comillas_pos]

    def __quote_directors(self):
        # Con procesamiento extraigo lo que puede ser un nombre
        nombres = self.extract_names(self.__ori_text)
        # Inicio una lista para buscar apariciones de los directores en el texto
        self.__ini_director_pos = []
        # Compruebo que el nombre corresponda con un director indexado
        for nombre in nombres:
            # Si ya he preguntado por este nombre paso al siguiente
            if nombre in self.__personajes:
                continue
            # Lo guardo como nombre ya preguntado
            self.__personajes.append(nombre)
            for director in self.__all_director:
                # No quiero citar dos veces el mismo director
                if director in self.__directors:
                    continue
                # No quiero citar al director actual
                if director == self.director:
                    continue
                # Puede que sólo esté escrito el apellido del director
                if not nombre.lower() in director.lower():
                    continue
                # Pido confirmación al usuario de la cita
                if not self.__ask_confirmation(nombre, director):
                    continue
                citation = {'pos': self.__ori_text.find(nombre),
                            'director': director,
                            'len': len(nombre)}
                self.__ini_director_pos.append(citation)
                # Lo guardo como director ya citado
                self.__directors.append(director)
                break

        # Ahora ya tengo los índices que quería
        for cit in self.__ini_director_pos:
            self.__add_director_link(cit)

        pass

    def __ask_confirmation(self, nombre, director):
        # Si son idénticos, evidentemente es una cita
        if nombre == director:
            return True
        # En caso contrario, pregunto
        pregunta = "¿Es {} una cita de {}? ".format(nombre, director)
        question = YesNo(pregunta)
        ans = question.get_ans()
        return bool(ans)

    def __add_director_link(self, cit):
        # Construyo el link
        dir = urllib.parse.quote(cit['director'])
        link = self.LINK_LABEL.format(dir)
        # Construyo el html para el enlace
        ini_link = self.OPEN_LINK.format(link)
        # Miro la posición dentro del texto
        position = cit['pos']
        self.__ori_text = insert_string_in_position(
            self.__ori_text, ini_link, position)
        # Actualizo la posición del cierre del hipervínculo
        position = position + cit['len'] + len(ini_link)
        self.__ori_text = insert_string_in_position(
            self.__ori_text, self.CLOSE_LINK, position)
        # Actualizo todo el resto de índices
        delta = len(ini_link) + len(self.CLOSE_LINK)
        for cit in self.__ini_director_pos:
            cit['pos'] = cit['pos'] + delta


    def __row_in_csv(self, title: str):
        for index, row in enumerate(self.__csv_reader):
            if title.lower() == row[0].lower().strip("\""):
                return index

        # No lo hemos encontrado
        return -1

    def extract_names(self, text):
        # Usando un procesador de lenguaje natural extraigo los nombres del párrafo
        texto_procesado = self.__nlp(text)

        personajes = []
        for ent in texto_procesado.ents:
            # Sólo lo añado a mi lista si la etiqueta asignada dice personaje
            if self.__is_person(ent):
                if ent.lemma_ not in personajes:
                    personajes.append(str(ent.lemma_))

        return personajes

    def __is_person(self, ent):
        # Aplico un correctivo a los Coen
        if ( ent.lemma_ == 'Coen' ):
            return True

        # Elimino los pronombres
        if (ent.lemma_ == 'yo'):
            return False

        # Caso general en el que me fio del modelo
        return ent.label_ == 'PER'

    def __get_directors_indexed(self):
        # Listamos los directores que hay en el csv asegurando una única ocurrencia de ellos
        self.__all_director = list(set([row[2] for row in self.__csv_reader]))


def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def insert_string_in_position(sr, sub, pos):
    return sr[:pos] + sub + sr[pos:]
