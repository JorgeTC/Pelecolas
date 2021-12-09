from src.dlg_config import manage_config


def main(path):

    manage_config()

    from src.WordReader import WordReader
    reader = WordReader(path)
    reader.list_titles()
    reader.write_list()

    print(len(reader.titulos))
    input("Press Enter to continue...")
