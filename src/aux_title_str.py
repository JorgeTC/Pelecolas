from datetime import date, time
import re


def split_title_year(title: str) -> tuple[str, str]:
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


RE_DATE_DMY = re.compile(r"^(1[0-9]|2[0-9]|3[0-1]|0?[1-9])(\.|-|/)"
                         r"(1[0-2]|0?[1-9])(\.|-|/)"
                         r"(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])$")
RE_DATE_YMD = re.compile(r"^(19[0-9][0-9]|20[0-9][0-9]|[0-9][0-9])(\.|-|/)"
                         r"(1[0-2]|0?[1-9])(\.|-|/)"
                         r"(1[0-9]|2[0-9]|3[0-1]|0?[1-9])")
RE_TIME = re.compile(r"([0-1]?[0-9]|2[0-3])(\.|-|/|:)"
                     r"([0-5][0-9])")


def date_from_YMD(string: str) -> date:
    if not (match := RE_DATE_YMD.match(string)):
        return None

    return date(int(match.group(1)),
                int(match.group(3)),
                int(match.group(5)))


def date_from_DMY(string: str) -> date:
    if not (match := RE_DATE_DMY.match(string)):
        return None

    return date(int(match.group(5)),
                int(match.group(3)),
                int(match.group(1)))


def time_from_str(string: str) -> time:
    if not (match := RE_TIME.match(string)):
        return None

    return time(int(match.group(1)),
                int(match.group(3)))


def DMY(ymd_date: str) -> str:
    '''
    Convierte una fecha con formato inglés (YMD)
    al formato español (DMY)
    '''
    return RE_DATE_YMD.sub(r"\5\4\3\2\1", ymd_date)
