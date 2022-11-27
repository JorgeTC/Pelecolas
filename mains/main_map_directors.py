import __init__
from collections import Counter
from src.excel.read_watched import read_watched
from src.progress_bar import ProgressBar


def main():
    # Creo una barra de progreso
    bar = ProgressBar()

    directors = Counter()
    for film, progress in read_watched(1742789):
        for director in film.director:
            directors.update({director: 1})
        bar.update(progress)
    print(directors.most_common())
    input()


if __name__ == '__main__':
    main()
