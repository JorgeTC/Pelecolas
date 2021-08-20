import docx
import nltk
from nltk.corpus import stopwords
from nltk import FreqDist
from nltk.tokenize import wordpunct_tokenize
from nltk.stem import WordNetLemmatizer

PATH="C:\\Users\\usuario\\Desktop\\Jorges things\\Reseñas\\Películas\\"
NAME="Películas.docx"

def get_full_text(parrfs):

    full_text = ""

    for parr in parrfs:
        full_text = full_text + parr + " "

    # No queremos el último espacio que hemos añadido de forma artificial
    return full_text[:-1]

def extract_text():
        # Abro el documento word
    file=docx.Document(PATH+NAME)

    # Extraigo en una lista todo el texto del documento
    parr_lis=[parr.text for parr in file.paragraphs if parr.text]

    # Extraigo el párrafo en el que he decidido trabajar
    my_parr = get_full_text(parr_lis[1:])
    # No quiero que haya sensibilidad a las mayúsculas.
    return my_parr.lower()

def list_words(my_parr):
    palabras_punct=nltk.tokenize.wordpunct_tokenize(my_parr)
    # Me deshago de signos de puntuación
    palabras_punct=[palabra for palabra in palabras_punct if palabra.isalpha()]
    # Me deshago de las palabras de parada
    ls_stopwords = stopwords.words("spanish")
    palabras_punct=[palabra for palabra in palabras_punct if not (palabra in ls_stopwords)]

    return palabras_punct

def desconjugar(palabras):
    return palabras

def get_frequencies(palabras):
    # Guardamos las frecuencias
    freq=FreqDist(palabras)

    # Ordeno las frecuencias
    freq = sorted(freq.items(), key=lambda item: item[1], reverse=True)

    return freq

if __name__ == "__main__":

    my_text = extract_text()

    palabras = list_words(my_text)

    freq = get_frequencies(palabras)

    for key,val in freq:
        print (str(key) + ':' + str(val))
