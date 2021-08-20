import docx
import nltk
import stanza
from nltk.corpus import stopwords
from nltk import FreqDist
import datetime
import sys

PATH="C:\\Users\\usuario\\Desktop\\Jorges things\\Reseñas\\Películas\\"
NAME="Películas.docx"

class Timer(object):
    def __init__(self):
        self.start = datetime.datetime.now()

    def remains(self, done):
        if done != 0:
            now  = datetime.datetime.now()
            left = (1 - done) * (now - self.start) / done
            sec = int(left.total_seconds())
            if sec < 60:
                return "{} seconds   ".format(sec)
            else:
                return "{} minutes   ".format(int(sec / 60))

class ProgressBar(object):
    def __init__(self):
        self.timer = Timer()
        self.barLength = 20
        self.progress = 0.0

    def update(self, done):
        self.progress = float(done)
        block = int(round(self.barLength * self.progress))
        text = "\r[{0}] {1:.2f}% {2}".format( "="*block + " "*(self. barLength-block), self. progress*100, self.timer.remains(self.progress))
        sys.stdout.write(text)
        sys.stdout.flush()

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
    parr_lis=[parr.text for parr in file.paragraphs[:10] if parr.text]

    del file

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
    new_dict = {}

    nlp = stanza.Pipeline("es", verbose=False)

    keys = [palabra[0] for palabra in palabras]
    total = len(keys)
    timer = ProgressBar()
    for index, pal in enumerate(keys):
        pal_doc = nlp(pal).sentences[0].words[0].lemma

        if pal_doc in new_dict.keys():
            new_dict[pal_doc] += palabras[index][1]
        else:
            new_dict[pal_doc] = palabras[index][1]

        timer.update(index/total)

    return new_dict

def get_frequencies(palabras):
    # Guardamos las frecuencias
    freq=FreqDist(palabras)

    # Ordeno las frecuencias
    freq = sorted(freq.items(), key=lambda item: item[1], reverse=True)

    return freq

def write_csv(freq_dict):

    output_file = open(PATH + "recuento.csv", "w")

    # Escribo los encabezados
    output_file.write("Palabra,ocurrencias\n")

    for key, val in freq_dict.items():
        output_file.write("{},{}\n".format(key, val))

    output_file.close()

if __name__ == "__main__":

    my_text = extract_text()

    palabras = list_words(my_text)
    # Hacemos una primera limpieza de palabras repetidas
    freq = get_frequencies(palabras)

    freq = desconjugar(freq)

    write_csv(freq)

    input("Espero enter")
