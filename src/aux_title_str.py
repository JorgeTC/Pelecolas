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


REGULAR_EXPRESSION_DATE = re.compile(r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)"
                                     r"([1-9]|0[1-9]|1[0-2])(\.|-|/)"
                                     r"([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$")
REGULAR_EXPRESSION_DATE_BLOG = re.compile(r"^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)"
                                          r"([1-9]|0[1-9]|1[0-2])(\.|-|/)"
                                          r"([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])")
