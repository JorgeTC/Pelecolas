import __init__
from src.essays.word import WordReader


def main():

    WordReader.list_titles()
    WordReader.write_list()

    print(len(WordReader.TITULOS))
    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
