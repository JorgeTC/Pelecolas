import __init__
from src.essays.dlg_scroll_titles import DlgScrollTitles
from src.essays.word import WordReader


def main():
    word_titles = WordReader.list_titles()
    dlg_title = DlgScrollTitles("Título para buscar: ", word_titles)
    title_to_search = dlg_title.get_ans()
    year = WordReader.find_year(title_to_search)
    print(year)


if __name__ == '__main__':
    main()
