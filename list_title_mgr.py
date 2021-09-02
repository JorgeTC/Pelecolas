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

        # Hago dos versiones más de la lista de títulos.
        # Uno en minísculas
        self.ls_lower = [title.lower() for title in self.ls_title]
        # Otro con los títulos normalizados
        self.ls_norm = [self.__normalize_string(title) for title in self.ls_lower]


        # defino los caracteres para los que no quiero que sea sensitivo
        self.__unwanted_chars = self.__make_unwanted_chars()

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
        # No quiero que sea sensible a las mayúsculas
        titulo = titulo.lower()

        for val in self.ls_title:
            if titulo == val.lower():
                # Caso de coincidencia exacta
                self.titulo = val
                return True

        # Si es posible, siguiero los títulos más cercanos al introducido
        self.__closest_title(titulo)

        return False

    def __closest_title(self, titulo):
        # Intento buscar los casos más cercanos
        titulo = self.__normalize_string(titulo)
        found = False
        # Recorro la lista de titulos
        for iter in self.ls_title:
            # Efectúo la comparación usando un título normalizado
            iter_ = self.__normalize_string(iter)
            # Busco si se contienen mutuamente
            if titulo.find(iter_) >= 0 or iter_.find(titulo) >= 0:
                # Hay suficiente concordancia como para sugerir el título
                if not found:
                    # Aún no he impreso nada por pantalla
                    print("Quizás quisiste decir...")
                    found = True
                # Imprimo el título original. El que se ha leído en el documento
                print(iter)

    def __normalize_string(self, str):
        # Elimino las mayúsculas
        str = str.lower()
        # Elimino espacios, signos de puntuación y acentos
        str = str.translate(self.__unwanted_chars)
        # Elimino caracteres repetidos
        str = re.sub(r'(.)\1+', r'\1', str)
        return str
