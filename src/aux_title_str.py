import re


def split_title_year(title: str):
    '''
    Dado un título de los escritos en el word,
    quiero extraer el posible año que tenga entre paréntesis
    '''
    # Cadena separada del paréntesis por al menos un espacio
    # En el paréntesis debe haber 4 dígitos
    has_year = re.match(r"(.+) +\((\d{4})\)", title)
    try:
        return has_year.group(2), has_year.group(1)
    except AttributeError:
        return "", title


RE_DATE_DMY = re.compile(r"^(1[0-9]|2[0-9]|3[0-1]|0?[1-9])(?:\.|-|/)"
                         r"(1[0-2]|0?[1-9])(?:\.|-|/)"
                         r"(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])$")
RE_DATE_YMD = re.compile(r"^(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(?:\.|-|/)"
                         r"(1[0-2]|0?[1-9])(?:\.|-|/)"
                         r"(1[0-9]|2[0-9]|3[0-1]|0?[1-9])")
RE_TIME = re.compile(r"([0-1]?[0-9]|2[0-3])(?:\.|-|/|:)"
                     r"([0-5][0-9])")
