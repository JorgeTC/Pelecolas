from collections import Counter

import __init__
from src.config import Config, Param, Section
from src.excel.read_watched import read_directors
from src.progress_bar import ProgressBar
from src.usuario import Usuario


def write_in_file(directors: list[tuple[str, int]], user_name: str):
    out_folder_path = Config.get_folder_path(
        Section.READDATA, Param.OUTPUT_EXCEL)
    out_file_path = out_folder_path / f"{user_name}.txt"
    with open(out_file_path, mode='w', encoding='utf-8') as output_file:
        for dir, repetitions in directors:
            line = f"{dir}: {repetitions}"
            try:
                output_file.write(line + "\n")
            except:
                print(line)


def main():
    usuario = Usuario.ask_user()

    # Creo una barra de progreso
    bar = ProgressBar()

    directors = Counter()
    for film, progress in read_directors(usuario.id):
        for director in film.directors:
            directors.update({director: 1})
        bar.update(progress)
    most_common = directors.most_common()

    write_in_file(most_common, usuario.nombre)


if __name__ == '__main__':
    main()
