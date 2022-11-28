import __init__
from collections import Counter
from src.excel.read_watched import read_watched
from src.progress_bar import ProgressBar
from src.usuario import Usuario


def write_in_file(directors: list[tuple[str, int]], user_name: str):
    with open(f"C:/Users/jdlat/Desktop/{user_name}.txt", mode='w', encoding='utf-8') as output_file:
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
    for film, progress in read_watched(usuario.id):
        for director in film.directors:
            directors.update({director: 1})
        bar.update(progress)
    most_common = directors.most_common()

    write_in_file(most_common, usuario.nombre)


if __name__ == '__main__':
    main()
