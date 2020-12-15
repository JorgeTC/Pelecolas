import requests
import webbrowser
import sys
from bs4 import BeautifulSoup
import time
import datetime
 
class Timer(object):
    def __init__(self):
        self.start = datetime.datetime.now()
 
    def remains(self, done):
        now  = datetime.datetime.now()
        left = (1 - done) * (now - self.start) / done
        sec = int(left.total_seconds())
        if sec < 60:
           return "{} seconds".format(sec)
        else:
           return "{} minutes".format(int(sec / 60))


def SafeGetUrl(url):
    #open with GET method 
    resp = requests.get(url)
    # Caso 429: too many requests
    if resp.status_code == 429:
        return PassCaptcha(url)
    else: # No está contemplado el caso 404: not found
        return resp

def PassCaptcha(url):
    # abro un navegador para poder pasar el Captcha
    webbrowser.open(url)
    resp = requests.get(url)
    print("\nPor favor, entra en FilmAffinity y pasa el captcha por mí.")
    # Controlo que se haya pasado el Captcha
    while resp.status_code == 429:
        time.sleep(3) # intento recargar la página cada 3 segundos
        resp = requests.get(url)
    return resp

def GetTotalFilms(resp):
    soup=BeautifulSoup(resp.text,'html.parser')
    # me espero que haya un único "value-box active-tab"
    mydivs = soup.find("a", {"class": "value-box active-tab"})
    stringNumber = mydivs.contents[3].contents[1]
    # Elimino el punto de los millares
    stringNumber = stringNumber.replace('.','')
    return int(stringNumber)

def update_progress(progress, timer):
    barLength = 20 # Modify this to change the length of the progress bar
    if isinstance(progress, int):
        progress = float(progress)
    block = int(round(barLength * progress))
    text = "\r[{0}] {1:.2f}% {2}".format( "="*block + " "*(barLength-block), progress*100, timer.remains(progress))
    sys.stdout.write(text)
    sys.stdout.flush()

def IndexToLine(index, total):
    return total - index + 1


def ReadWatched(IdUser, f):
    DataIndex = 0 # contador de peliculas
    nIndex = 1 # numero de pagina actual
    Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
    resp = SafeGetUrl(Vistas)

    totalFilms = GetTotalFilms(resp)
    timer = Timer()
    while (DataIndex < totalFilms):

        # we need a parser,Python built-in HTML parser is enough . 
        soup = BeautifulSoup(resp.text,'html.parser')
        # Guardo en una lista todas las películas de la página nIndex-ésima
        mylist = soup.findAll("div", {"class": "user-ratings-movie"})

        for i in mylist:
            # La votacion del usuario la leo desde fuera
            # no puedo leer la nota del usuario dentro de la ficha
            #guardo la url de la ficha de la pelicula
            url = i.contents[1].contents[1].contents[3].contents[3].contents[0].attrs['href']
            #Entro a la ficha y leo votacion popular, duracion y votantes
            url = url.split('/film')[1]
            url = url.split('.html')[0]
            f.write(url + "\n")
            DataIndex +=1
            # actualizo la barra de progreso
            update_progress(DataIndex/totalFilms, timer)

        # Siguiente pagina del listado
        nIndex += 1
        Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
        resp = SafeGetUrl(Vistas)


if __name__ == "__main__":
    Ids = {'Sasha': 1230513, 'Jorge': 1742789, 'Guillermo': 4627260, 'Daniel Gallego': 983049, 'Luminador': 7183467,
    'Will_llermo': 565861, 'Roger Peris': 3922745, 'Javi': 247783}
    usuario = 'Will_llermo'
    print("Se van a importar los datos de ", usuario)
    input("Espero Enter...")
    Plantilla = 'Plantilla.xlsx'
    ExcelName = 'Ides - ' + usuario + '.txt'
    textFile = open(ExcelName, "w")
    ReadWatched(Ids[usuario], textFile)
    textFile.close()
