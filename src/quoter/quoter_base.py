from src.blog_csv_mgr import BlogCsvMgr


class QuoterBase:
    INI_QUOTE_CHAR = "“"
    FIN_QUOTE_CHAR = "”"

    OPEN_LINK = "<a href=\"{}\">".format
    CLOSE_LINK = "</a>"
    LINK_LABEL = "https://pelecolas.blogspot.com/search/label/{}".format

    # Compruebo si tengo un csv actualizado.
    # En caso contrario, lo escribo
    if BlogCsvMgr.is_needed():
        BlogCsvMgr.write_csv()
    # Lector de csv
    CSV_CONTENT = BlogCsvMgr.open_to_read()


def find(s: str, ch: str) -> list[int]:
    return [i for i, ltr in enumerate(s) if ltr == ch]


def insert_string_in_position(sr: str, sub: str, pos: int) -> str:
    return sr[:pos] + sub + sr[pos:]
