from contextlib import contextmanager
from pathlib import Path

from src.essays.word.word_folder_mgr import get_files
from src.essays.word.word_reader import (WordReader, init_paragraphs,
                                         init_titles)


@contextmanager
def set_word_folder(word_folder: Path):

    # Guardo los valores que tendré que reestablecer
    original_titles = WordReader.TITULOS
    original_year_parrs = WordReader.YEARS_PARR
    original_paragraphs = WordReader.PARAGRAPHS

    # Escribo los valores con la actual carpeta de Word
    words = get_files(word_folder)
    WordReader.PARAGRAPHS, WordReader.YEARS_PARR = init_paragraphs(words)
    WordReader.TITULOS = init_titles(WordReader.HEADER, WordReader.PARAGRAPHS)

    try:
        yield
    finally:
        # Devuelvo el valor original
        WordReader.TITULOS = original_titles
        WordReader.YEARS_PARR = original_year_parrs
        WordReader.PARAGRAPHS = original_paragraphs
