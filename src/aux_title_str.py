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
