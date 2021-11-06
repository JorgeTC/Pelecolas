from .WordReader import WordReader

def main(path):
    reader = WordReader(path)
    reader.list_titles()
    reader.write_list()

    print(len(reader.titulos))
    input("Press Enter to continue...")