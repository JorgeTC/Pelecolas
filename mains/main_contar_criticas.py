from src.config import manage_config


def main():

    manage_config()

    from src.word import WordReader

    WordReader.list_titles()
    WordReader.write_list()

    print(len(WordReader.TITULOS))
    input("Press Enter to continue...")
