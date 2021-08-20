import docx
import nltk

PATH="C:\\Users\\usuario\\Desktop\\Jorges things\\Reseñas\\Películas\\"
NAME="Películas.docx"

if __name__ == "__main__":
    # Abro el documento word
    file=docx.Document(PATH+NAME)

    # Extraigo en una lista todo el texto del documento
    parr_lis=[parr.text for parr in file.paragraphs if parr.text]

    # Extraigo el párrafo en el que he decidido trabajar
    my_parr = parr_lis[2].lower()

    # Vamos a intentar tratar sólo el primer párrafo
    palabras = nltk.tokenize.word_tokenize(my_parr)

    # Guardamos las frecuencias
    freq=nltk.FreqDist(palabras)

    # Ordeno las frecuencias
    freq = sorted(freq.items(), key=lambda item: item[1], reverse=True)

    for key,val in freq:
        print (str(key) + ':' + str(val))
