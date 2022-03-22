from src.dlg_config import manage_config


def main(path):

    manage_config()

    from src.word_reader import WordReader
    reader = WordReader()
    reader.list_titles()
    reader.write_list()

    print(len(reader.titulos))
    input("Press Enter to continue...")
