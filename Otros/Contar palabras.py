import docx
import nltk
import stanza
from nltk.corpus import stopwords
from nltk import FreqDist
import datetime
import sys
import torch

PATH="C:\\Users\\usuario\\Desktop\\Jorges things\\Reseñas\\Películas\\"
NAME="Películas.docx"

MODEL_FOLDER="C:\\Users\\usuario\\stanza_resources\\es\\lemma\\"

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

    def __del__(self):
        self.update(1)
        del self.timer

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
    parr_lis=[parr.text for parr in file.paragraphs[:] if parr.text]

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

class Desconjugador:
    def __init__(self, palabras) -> None:
        # No es un diccionario, es una lista de pares
        self.palabras = palabras

        self.__emprove_lemma()

        self.nlp = stanza.Pipeline('es', package='ancora',
                                    processors='tokenize,pos,lemma',
                                    lemma_model_path=MODEL_FOLDER+'ancora_customized.pt',
                                    verbose=False)

        pass

    def __emprove_lemma(self):

        model = torch.load(MODEL_FOLDER + "ancora.pt", map_location='cpu')

        self.word_dict, self.composite_dict = model['dicts']

        self.__add_word('peli', 'película', 'NOUN')
        self.__add_word('pelis', 'película', 'NOUN')
        self.__add_word('dirigido', 'dirigir', 'VERB')
        self.__add_word('zooms', 'zoom', 'NOUN')
        self.__add_word('ciges', 'Ciges', 'PROPN')
        self.__add_word('camarera', 'camarero', 'NOUN')
        self.__add_word('famosísimo', 'famoso', 'ADJ')
        self.__add_word('famosísimos', 'famoso', 'ADJ')
        self.__add_word('famosísima', 'famoso', 'ADJ')
        self.__add_word('famosísimas', 'famoso', 'ADJ')
        self.__add_word('delgadísimo', 'delgado', 'ADJ')
        self.__add_word('correctísimo', 'correcto', 'ADJ')
        self.__add_word('larguísimo', 'largo', 'ADJ')
        self.__add_word('primerísimo', 'primero', 'ADJ')
        self.__add_word('vuelca', 'volcar', 'VERB')
        self.__add_word('puesta', 'puesto', 'ADJ')
        self.__add_word('chica', 'chico', 'NOUN')
        self.__add_word('niña', 'niño', 'NOUN')
        self.__add_word('hombrecillo', 'hombre', 'NOUN')
        self.__add_word('muchísimos', 'mucho', 'ADJ')
        self.__add_word('muchísimo', 'mucho', 'ADJ')
        self.__add_word('sacarla', 'sacar', 'VERB')
        self.__add_word('tenerla', 'tener', 'VERB')
        self.__add_word('adornarla', 'adornar', 'VERB')
        self.__add_word('cansarla', 'cansar', 'VERB')
        self.__add_word('seducirla', 'seducir', 'VERB')
        self.__add_word('moverlo', 'mover', 'VERB')
        self.__add_word('oírla', 'oír', 'VERB')
        self.__add_word('grabarla', 'grabar', 'VERB')
        self.__add_word('grabarlo', 'grabar', 'VERB')
        self.__add_word('verlo', 'ver', 'VERB')
        self.__add_word('verla', 'ver', 'VERB')
        self.__add_word('verle', 'ver', 'VERB')
        self.__add_word('serlo', 'ser', 'VERB')
        self.__add_word('tenerlo', 'tener', 'VERB')
        self.__add_word('ayudarla', 'ayudar', 'VERB')
        self.__add_word('admitirle', 'admitir', 'VERB')
        self.__add_word('admitirlo', 'admitir', 'VERB')
        self.__add_word('decirle', 'decir', 'VERB')
        self.__add_word('decirlo', 'decir', 'VERB')
        self.__add_word('decirla', 'decir', 'VERB')
        self.__add_word('dárselo', 'dar', 'VERB')
        self.__add_word('haberla', 'haber', 'VERB')
        self.__add_word('hacerlo', 'hacer', 'VERB')
        self.__add_word('hacérselo', 'hacer', 'VERB')
        self.__add_word('creyéndose', 'creer', 'VERB')
        self.__add_word('imponérselo', 'imponer', 'VERB')
        self.__add_word('quedárselo', 'quedar', 'VERB')
        self.__add_word('intercalarse', 'intercalar', 'VERB')
        self.__add_word('decirse', 'decir', 'VERB')
        self.__add_word('romperse', 'romper', 'VERB')
        self.__add_word('rompiéndose', 'romper', 'VERB')


        torch.save(model, MODEL_FOLDER + 'ancora_customized.pt')

        pass

    def __add_word(self, word, lema, category):
        self.composite_dict[(word, category)] = lema
        self.word_dict[word] = lema

    def desconjugar(self):

        new_dict = {}

        nlp = stanza.Pipeline('es', package='ancora', processors='tokenize,pos,lemma', lemma_model_path=MODEL_FOLDER+'ancora_customized.pt', verbose=False)

        keys = [palabra[0] for palabra in self.palabras]
        total = len(keys)
        timer = ProgressBar()
        for index, pal in enumerate(keys):

            # Si la palabra es una única letra, no nos da información
            if( len(pal) == 1 ):
                pass

            pal_doc = nlp(pal).sentences[0].words[0].lemma

            if pal_doc in new_dict.keys():
                new_dict[pal_doc] += self.palabras[index][1]
            else:
                new_dict[pal_doc] = self.palabras[index][1]

            timer.update(index/total)
        del timer

        self.palabras = sort_dict(new_dict)


def sort_dict(freq):
    return sorted(freq.items(), key=lambda item: item[1], reverse=True)

def get_frequencies(palabras):
    # Guardamos las frecuencias
    freq=FreqDist(palabras)

    # Ordeno las frecuencias
    freq = sort_dict(freq)

    return freq

def write_csv(freq_dict):

    output_file = open(PATH + "recuento.csv", "w")

    # Escribo los encabezados
    output_file.write("Palabra,ocurrencias\n")

    for key, val in freq_dict:
        output_file.write("{},{}\n".format(key, val))

    output_file.close()

if __name__ == "__main__":

    my_text = extract_text()

    palabras = list_words(my_text)
    # Hacemos una primera limpieza de palabras repetidas
    freq = get_frequencies(palabras)

    nlp = Desconjugador(freq)
    nlp.desconjugar()

    write_csv(nlp.palabras)

    input("Espero enter")
