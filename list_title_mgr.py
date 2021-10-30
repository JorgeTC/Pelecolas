import re

# Clase para hallar el título más próximo.
# Cuando se inserta intítulo por teclado trato de buscar el título más parecido
# de las reseñas que hay escritas.


class TitleMgr():
    def __init__(self, title_list):
        # Copio todos los títulos disponibles.
        # La clase html los tiene en forma de diccionario.
        # Yo sólo necesito las llaves de ese diccionario.
        self.ls_title = title_list

        # defino los caracteres para los que no quiero que sea sensitivo
        # necesario para la operación de normalización.
        self.__unwanted_chars = self.__make_unwanted_chars()

        # Hago dos versiones más de la lista de títulos.
        # Uno en minísculas
        self.ls_lower = [title.lower() for title in self.ls_title]
        # Otro con los títulos normalizados
        self.ls_norm = [self.__normalize_string(title) for title in self.ls_lower]


        # Variables para guardar el resultado del cálculo.
        self.__exists = False
        self.__position = -1
        # Indices para cuando haya que sugerir resultados
        self.__lsn_suggestions = []

    def __make_unwanted_chars(self):

        # No quiero que los caracteres de puntuación afecten al buscar la película
        chars_dict = dict.fromkeys(map(ord, " ,!¡@#$?¿()."), None)
        # Elimino los tipos de tildes
        chars_dict.update(zip(map(ord, "áéíóú"), map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "àèìòù"), map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "âêîôû"), map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "äëïöü"), map(ord, "aeiou")))

        return chars_dict

    def exists(self, titulo):

        # Inicio las variables de búsqueda
        self.__exists = False
        self.__position = -1
        self.__lsn_suggestions.clear()

        # No quiero que sea sensible a las mayúsculas
        titulo = titulo.lower()

        for i, val in enumerate(self.ls_lower):
            if titulo == val:

                # Guardo el booleano para el caché
                self.__exists = True
                # Guardo la posición para saber cuál es la llave que le corresponde
                self.__position = i
                return True

        # Si es posible, siguiero los títulos más cercanos al introducido
        self.__closest_title(titulo)

        return False

    def __closest_title(self, titulo):
        # Intento buscar los casos más cercanos
        titulo = self.__normalize_string(titulo)

        # Recorro la lista de titulos
        for index, normalized in enumerate(self.ls_norm):

            # Busco si se contienen mutuamente
            if titulo.find(normalized) >= 0 or normalized.find(titulo) >= 0:
                # Hay suficiente concordancia como para sugerir el título
                self.__lsn_suggestions.append(index)

        # Si he encontrado titulos para sugerir, los imprimo
        if not self.__lsn_suggestions:
            return
        self.print()

    def __normalize_string(self, str):
        # Elimino las mayúsculas
        str = str.lower()
        # Elimino espacios, signos de puntuación y acentos
        str = str.translate(self.__unwanted_chars)
        # Elimino caracteres repetidos
        str = re.sub(r'(.)\1+', r'\1', str)
        return str

    def exact_key(self, title):

        self.exists(title)

        # Variables exists y position ya calculadas.
        if self.__exists:
            return self.ls_title[self.__position]
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
            print(self.ls_title[index])

    def get_suggested_titles_count(self):
        return len(self.__lsn_suggestions)

    def get_suggested_title(self, index):
        # Obtengo la posición que el indexésimo título ocupa en la lista de títulos
        suggested_index = self.__lsn_suggestions[index]
        # Devuelvo el título
        return self.ls_title[suggested_index]
