from logging import exception
from types import CodeType
import requests
import webbrowser
# from openpyxl.styles import PatternFill, Border, Side, numbers
import sys
from bs4 import BeautifulSoup
import time
import datetime
import csv

class Timer(object):
    def __init__(self):
        self.start = datetime.datetime.now()

    def remains(self, done):
        if done != 0:
            now  = datetime.datetime.now()
            left = (1 - done) * (now - self.start) / done
            sec = int(left.total_seconds())
            if sec < 60:
                return "{} seconds".format(sec)
            else:
                return "{} minutes".format(int(sec / 60))

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
    while resp.status_code != 200:
        time.sleep(3) # intento recargar la página cada 3 segundos
        resp = requests.get(url)
    return resp

def DeleteBrackets(year):
    year = year.replace('(I)', '')
    year = year.replace('(II)', '')
    year = year.replace('(', '')
    year = year.replace(')', '')
    return year

def CrearLista():
    enlace_base = "https://www.imdb.com/list/ls070809143/?sort=list_order,asc&st_dt=&mode=detail&page="
    films = 0
    bar = ProgressBar()
    csv_name = 'Rosenbaum.csv'
    file = open(csv_name, mode = 'w')
    fieldnames = ['Titulo', 'Año', 'Director']
    writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter = ';', lineterminator='\n')
    writer.writeheader()
    for index in range(1, 11):
        curr_url = enlace_base + str(index)
        resp = SafeGetUrl(curr_url)
        soup = BeautifulSoup(resp.text,'html.parser')
        pelis = soup.findAll("div", {"class": "lister-item-content"})
        for i in pelis:
            titulo = i.contents[1].parent.contents[1].contents[3].contents[0]
            try:
                año = int(DeleteBrackets(i.contents[1].contents[5].contents[0]))
            except:
                pass
            try:
                director = i.contents[9].contents[1].contents[0]
            except:
                director = i.contents[11].contents[1].contents[0]

            writer.writerow({'Titulo': titulo, 'Año': año, 'Director': director})

            films = films + 1
            bar.update(films/1000)

def ColumnaDeVistas():
    try:
        lista = open('Rosenbaum.csv', 'r')
    except:
        # Si no existe el archivo con las películas ya vistas, lo creo
        CrearLista()
        lista = open('Rosenbaum.csv', 'r')
    lista_si_vista = open('Rosenbaum vistas.csv', mode = 'w')
    reader = csv.reader(lista, delimiter=';', lineterminator='\n')
    campos = ["Titulo", "Año", "Director", "Vista"]
    writer = csv.DictWriter(lista_si_vista, fieldnames=campos, delimiter=';', lineterminator='\n')
    lineas = []

    lectura = list(reader)
    i = 0
    while i < len(lectura):
        if lectura[i][0] == str('Titulo'):
            writer.writeheader()
        else:
            pregunta = "\"" + lectura[i][0] + "\" del año " + str(lectura[i][1]) + " de " + lectura[i][2] + "\n"
            vista = input(pregunta)
            if vista == '' or vista == '0':
                vista = 0
            elif vista == '200':
                lineas.pop()
                i = i - 1
                continue
            else:
                vista = 1

            lineas.append({"Titulo": lectura[i][0], 'Año': lectura[i][1], 'Director': lectura[i][2], 'Vista': vista})

        i = i + 1

    writer.writerows(lineas)



if __name__ == "__main__":
    ColumnaDeVistas()
