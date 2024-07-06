from io import StringIO

import __init__
from src.essays.html.dlg_make_html import DlgScrollTitles
from src.essays.word import WordReader


def get_film_text(essay_title: str) -> str:
    # Inicializo el texto
    text = StringIO()
    for paragraph in WordReader.iter_review(essay_title):
        for run in paragraph.runs:
            text.write(run.text)
        text.write("\n")
    return text.getvalue()


def ask_title() -> str:
    ASK_TITLE = "Introduzca título de la película: "
    titles = WordReader.list_titles()
    dialog = DlgScrollTitles(ASK_TITLE, titles)
    return dialog.get_ans()


def main():
    essay_title = ask_title()
    print(get_film_text(essay_title))


if __name__ == '__main__':
    main()
