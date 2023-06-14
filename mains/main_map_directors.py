import csv

import __init__
from src.config import Config, Param, Section
from src.gui import ProgressBar
from src.scrap_fa import ReadWatched, UserFA


def write_in_file(directors: dict[str, list[int]], user_name: str):
    out_folder_path = Config.get_folder_path(Section.READDATA, Param.OUTPUT_EXCEL)
    out_file_path = out_folder_path / f"{user_name}.csv"

    rows = ((director, len(notes), round(sum(notes) / len(notes), 2))
            for director, notes in directors.items())

    with open(out_file_path, mode='w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Director', 'FilmsSeen', 'AverageNote'])
        csv_writer.writerows(rows)


def main():
    user = UserFA.ask_user()

    # Creo una barra de progreso
    bar = ProgressBar()

    directors: dict[str, list[int]] = {}
    for film, progress in ReadWatched.read_directors(user.id):
        for director in film.directors:
            directors.setdefault(director, []).append(film.user_note)
        bar.update(progress)

    write_in_file(directors, user.name)


if __name__ == '__main__':
    main()
