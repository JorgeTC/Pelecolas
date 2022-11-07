import re


def make_unwanted_chars() -> dict[int, int | None]:

    # No quiero que los caracteres de puntuación afecten al buscar la película
    chars_dict = dict.fromkeys(map(ord, " ,!¡@#$?¿()."), None)
    # Elimino los tipos de tildes
    chars_dict.update(zip(map(ord, "áéíóú"), map(ord, "aeiou")))
    chars_dict.update(zip(map(ord, "àèìòù"), map(ord, "aeiou")))
    chars_dict.update(zip(map(ord, "âêîôû"), map(ord, "aeiou")))
    chars_dict.update(zip(map(ord, "äëïöü"), map(ord, "aeiou")))

    return chars_dict


def normalize_string(string: str, *, UNWANTED_CHARS=make_unwanted_chars()) -> str:
    # Elimino las mayúsculas
    string = string.lower()
    # Elimino espacios, signos de puntuación y acentos
    string = string.translate(UNWANTED_CHARS)
    # Elimino caracteres repetidos
    string = re.sub(r'(.)\1+', r'\1', string)
    return string


class TitleMgr:
    # Clase para hallar el título más próximo.
    # Cuando se inserta un título por teclado trato de buscar el título más parecido
    # de las reseñas que hay escritas.

    def __init__(self, title_list: list[str]):
        # Copio todos los títulos disponibles.
        # La clase html los tiene en forma de diccionario.
        # Yo sólo necesito las llaves de ese diccionario.
        self.TITLES: list[str] = list(title_list)

        # Hago dos versiones más de la lista de títulos.
        # Uno en minísculas
        self.LOWER_TITLES: list[str] = [title.lower() for title in self.TITLES]
        # Otro con los títulos normalizados
        self.NORMALIZED_TITLES: list[str] = [normalize_string(title)
                                             for title in self.LOWER_TITLES]

        # Variables para guardar el resultado del cálculo.
        self.__exists: bool = False
        self.__position: int = -1
        # Indices para cuando haya que sugerir resultados
        self.__lsn_suggestions: list[int] = []

    def is_title_in_list(self, titulo: str) -> bool:
        '''
        Devuelve `True` si el argumento introducido se encuentra
        exactamente así (salvo mayúsculas) en la lista de títulos.
        '''

        # Inicio las variables de búsqueda
        self.__lsn_suggestions.clear()

        # No quiero que sea sensible a las mayúsculas
        titulo = titulo.lower()

        try:
            # Guardo la posición para saber cuál es la llave que le corresponde
            self.__position = self.LOWER_TITLES.index(titulo)
        except ValueError:
            self.__position = -1

        # Si he encontrado el elemento, seguro que existe
        self.__exists = (self.__position >= 0)
        return self.__exists

    def exists(self, titulo: str) -> bool:

        # Si el título está en la lista, puedo salir de aquí
        if self.is_title_in_list(titulo):
            return True

        # De lo contrario y si es posible, sugiero los títulos más cercanos al introducido
        self.__closest_title(titulo)
        return False

    def __closest_title(self, titulo: str):
        # Intento buscar los casos más cercanos
        titulo = normalize_string(titulo)

        # Guardo las posiciones de los títulos que tengan suficiente coincidencia.
        # Esto significa que o bien lo introducido esté contenido en el título o viceversa
        self.__lsn_suggestions = \
            [index
             for index, normalized in enumerate(self.NORMALIZED_TITLES)
             if titulo.find(normalized) >= 0 or normalized.find(titulo) >= 0]

        # Si he encontrado títulos para sugerir, los imprimo
        if self.__lsn_suggestions:
            self.print()

    def exact_key(self, title: str) -> str:

        self.exists(title)

        # Variables exists y position ya calculadas.
        if self.__exists:
            return self.TITLES[self.__position]
        else:
            # Ya sé que no está en la lista de llaves.
            return ""

    def exact_key_without_dlg(self, title: str) -> str:

        # Calculo las variables exists y position
        self.is_title_in_list(title)

        # Variables exists y position ya calculadas.
        if self.__exists:
            return self.TITLES[self.__position]
        else:
            # Ya sé que no está en la lista de llaves.
            return ""

    def print(self):

        # Si no tengo sugerencias que hacer, no imprimo nada
        if not self.__lsn_suggestions:
            return

        print("Quizás quisiste decir...")
        for index in self.__lsn_suggestions:
            # Imprimo el título original. El que se ha leído en el documento
            print(self.TITLES[index])

    @property
    def suggestions(self) -> list[str]:
        return [self.TITLES[index] for index in self.__lsn_suggestions]
