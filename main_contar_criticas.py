from .WordReader import WordReader
import keyboard


def main(path):

    if keyboard.is_pressed('ctrl'):
        from .dlg_config import DlgConfig
        config = DlgConfig()
        config.run()

    reader = WordReader(path)
    reader.list_titles()
    reader.write_list()

    print(len(reader.titulos))
    input("Press Enter to continue...")