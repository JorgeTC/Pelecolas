import random
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


class TitleEntry:
    def __init__(self, title: str):
        self.title = title
        self.lower = title.lower()
        self.normalized = normalize_string(title)


class TitleMgr:
    def __init__(self, title_list: list[str]):
        self.titles = [TitleEntry(title) for title in title_list]

    def is_title_in_list(self, titulo: str) -> bool:
        try:
            self.find_title_in_list(titulo)
        except StopIteration:
            return False
        return True

    def find_title_in_list(self, title: str) -> str:
        title = title.lower()
        return next(entry_title.title for entry_title in self.titles
                    if title == entry_title.lower)

    def exists(self, titulo: str) -> bool:
        if self.is_title_in_list(titulo):
            return True
        self.print_suggestions(titulo)
        return False

    def print_suggestions(self, title: str):
        suggestions = self.suggestions(title)
        if not suggestions:
            return
        print("Quizás quisiste decir...")
        for suggestion in suggestions:
            print(suggestion)

    def exact_key(self, title: str, *,
                  print_titles: bool = True, no_except: bool = True) -> str:
        try:
            exact_title = self.find_title_in_list(title)
        except StopIteration as e:
            if print_titles:
                self.print_suggestions(title)

            if no_except:
                return ""
            else:
                raise e
        return exact_title

    def suggestions(self, title: str) -> list[str]:
        # If user asks for a random option, provide it
        if (title == '--r'):
            return [random.choice(self.titles).title]

        title = normalize_string(title)

        return [entry_title.title
                for entry_title in self.titles
                if title in entry_title.normalized or entry_title.normalized in title]

    def list_titles(self) -> list[str]:
        return [entry_title.title for entry_title in self.titles]
