import __init__
from collections import Counter
from src.excel.read_watched import read_watched
from src.progress_bar import ProgressBar
from src.usuario import Usuario


def main():
    usuario = Usuario.ask_user()

    # Creo una barra de progreso
    bar = ProgressBar()

    directors = Counter()
    for film, progress in read_watched(usuario.id):
        for director in film.director:
            directors.update({director: 1})
        bar.update(progress)
    most_common = directors.most_common()
    for dir, repetitions in most_common:
        print(f"{dir}: {repetitions}")
    input()


if __name__ == '__main__':
    main()
