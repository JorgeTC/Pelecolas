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



        # Variables caché, para no repetir cálculos para un mismo título
        self.__titulo = ""
        self.__exists = False
        self.__position = -1

    def __make_unwanted_chars(self):

        # No quiero que los caracteres de puntuación afecten al buscar la película
        chars_dict = dict.fromkeys(map(ord, " ,!¡@#$?¿()."), None)
        # Elimino los tipos de tildes
        chars_dict.update(zip(map(ord, "áéíóú"),map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "àèìòù"),map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "âêîôû"),map(ord, "aeiou")))
        chars_dict.update(zip(map(ord, "äëïöü"),map(ord, "aeiou")))

        return chars_dict

    def exists(self, titulo):

        # Miro el caché para no buscar algo que ya haya buscado
        if titulo == self.__titulo:
            return self.__exists
        else:
            self.__titulo = titulo

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
        found = False
        # Recorro la lista de titulos
        for ori, normalized in zip(self.ls_title, self.ls_norm):

            # Busco si se contienen mutuamente
            if titulo.find(normalized) >= 0 or normalized.find(titulo) >= 0:
                # Hay suficiente concordancia como para sugerir el título
                if not found:
                    # Aún no he impreso nada por pantalla
                    print("Quizás quisiste decir...")
                    found = True
                # Imprimo el título original. El que se ha leído en el documento
                print(ori)

    def __normalize_string(self, str):
        # Elimino las mayúsculas
        str = str.lower()
        # Elimino espacios, signos de puntuación y acentos
        str = str.translate(self.__unwanted_chars)
        # Elimino caracteres repetidos
        str = re.sub(r'(.)\1+', r'\1', str)
        return str

    def exact_key(self, title):
        # Me espero que me den el mismo título cuya existencia ya he comprobado
        if title != self.__titulo:
            self.exists(title)

        # Variables exists y position ya calculadas.
        if self.__exists:
            return self.ls_title[self.__position]
        else:
            # Ya sé que no está en la lista de llaves.
            return ""
