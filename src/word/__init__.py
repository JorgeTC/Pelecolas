from src.word.pdf_writer import PDFWriter
from src.word.word_reader import WordReader

LIST_TITLES = WordReader.list_titles()

__all__ = [PDFWriter, WordReader, LIST_TITLES]