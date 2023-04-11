import csv

import __init__
from src.config import Config, Param, Section
from src.gui import ProgressBar
from src.scrap_fa import ReadWatched, UserFA


def write_in_file(directors: dict[str, tuple[int, list[float]]], user_name: str):
    out_folder_path = Config.get_folder_path(
        Section.READDATA, Param.OUTPUT_EXCEL)
    out_file_path = out_folder_path / f"{user_name}.csv"

    rows = []
    for dir, vals in directors.items():
        repetitions, notes = vals
        avg = sum(notes) / len(notes)
        rows.append([dir, repetitions, round(avg, 2)])

    with open(out_file_path, mode='w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Director', 'FilmsSeen', 'AverageNote'])
        csv_writer.writerows(rows)


def main():
    usuario = UserFA.ask_user()

    # Creo una barra de progreso
    bar = ProgressBar()

    directors: dict[str, tuple[int, list[float]]] = {}
    for film, progress in ReadWatched.read_directors(usuario.id):
        for director in film.directors:
            if director not in directors:
                directors[director] = [1, [film.user_note]]
            else:
                directors[director][0] += 1
                directors[director][1].append(film.user_note)
        bar.update(progress)

    write_in_file(directors, usuario.name)


if __name__ == '__main__':
    main()
