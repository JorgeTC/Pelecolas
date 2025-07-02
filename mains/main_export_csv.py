import csv

import __init__
from src.config import Config, Param, Section
from src.scrap_fa import ReadWatched, UserFA
from src.pelicula import Pelicula

def make_directors_list(list_directors: list[str]) -> str:
    return ",".join(list_directors)

def write_in_file(films: list[Pelicula], user_name: str):
    out_folder_path = Config.get_folder_path(Section.READDATA, Param.OUTPUT_EXCEL)
    out_file_path = out_folder_path / f"{user_name}.csv"



    rows = ((film.titulo, make_directors_list(film.directors), film.año, film.user_note/2)
            for film in films)

    with open(out_file_path, mode='w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Title', 'Directors', 'Year', 'Rating'])
        csv_writer.writerows(rows)


def main():
    user = UserFA.ask_user()

    films = (film for film, _ in ReadWatched.read_data(user.id))

    write_in_file(films, user.name)


if __name__ == '__main__':
    main()
