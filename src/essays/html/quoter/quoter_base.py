from ..blog_csv_mgr import BlogCsvMgr
from .lazy_initializer import LazyInitializer


class QuoterBase:
    INI_QUOTE_CHAR = "“"
    FIN_QUOTE_CHAR = "”"

    OPEN_LINK = "<a href=\"{}\">".format
    CLOSE_LINK = "</a>"
    LINK_LABEL = "https://pelecolas.blogspot.com/search/label/{}".format

    csv_content = LazyInitializer(BlogCsvMgr.get_updated_csv_content)


def find(s: str, ch: str) -> list[int]:
    return [i for i, ltr in enumerate(s) if ltr == ch]


def insert_string_in_position(sr: str, sub: str, pos: int) -> str:
    return sr[:pos] + sub + sr[pos:]
