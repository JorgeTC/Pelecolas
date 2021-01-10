import requests
import webbrowser
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
# from openpyxl.styles import PatternFill, Border, Side, numbers
import sys
from bs4 import BeautifulSoup
import time
import datetime

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

class Pelicula(object):
    def __init__(self, urlFA = None):
            self.url_FA = str(urlFA)
            resp = SafeGetUrl(self.get_FA_url())
            if resp.status_code == 404:
                self.exists = False
                return # Si el id no es correcto, dejo de construir la clase
            else:
                self.exists = True

            # Parseo la página
            self.parsed_page = BeautifulSoup(resp.text,'html.parser')

            self.nota_FA = None
            self.votantes_FA = None
            self.duracion = None

    def get_FA_url(self):
        return self.url_FA

    def GetTimeAndFA(self):
        # Comienzo a leer datos de la página
        l = self.parsed_page.find(id="movie-rat-avg")
        try:
            # guardo la nota de FA en una ficha normal
            self.nota_FA = float(l.attrs['content'])
        except:
            # caso en el que no hay nota de FA
            self.nota_FA = 0

        l = self.parsed_page.find(itemprop="ratingCount")
        try:
            # guardo la cantidad de votantes en una ficha normal
            self.votantes_FA = l.attrs['content']
            # Elimino el punto de los millares
            self.votantes_FA = self.votantes_FA.replace('.','')
            self.votantes_FA = int(self.votantes_FA)
        except:
            # caso en el que no hay suficientes votantes
            self.votantes_FA = 0

        l = self.parsed_page.find(id = "left-column")
        try:
            self.duracion = l.find(itemprop="duration").contents[0]
        except:
            # caso en el que no está escrita la duración
            self.duracion = "0"
        # quito el sufijo min.
        self.duracion = int(self.duracion.split(' ', 1)[0])

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

def SetCellValue(ws, line, col, value):
    cell = ws.cell(row = line, column=col)
    cell.value = value
    # Configuramos el estilo de la celda
    if (col == 5): # visionados. Ponemos punto de millar
        cell.number_format = '#,##0'
    elif (col == 9): # booleano mayor que
        cell.number_format = '0'
        cell.font = Font(name = 'SimSun', bold = True)
        cell.alignment=Alignment(horizontal='center', vertical='center')
    elif (col == 10):
        cell.number_format = '0.0'
    elif (col == 11 or col == 12): #reescala
        cell.number_format = '0.00'

def GetTotalFilms(resp):
    soup=BeautifulSoup(resp.text,'html.parser')
    # me espero que haya un único "value-box active-tab"
    mydivs = soup.find("a", {"class": "value-box active-tab"})
    stringNumber = mydivs.contents[3].contents[1]
    # Elimino el punto de los millares
    stringNumber = stringNumber.replace('.','')
    return int(stringNumber)

def IndexToLine(index, total):
    return total - index + 1


def ReadWatched(IdUser, ws):
    DataIndex = 0 # contador de peliculas
    nIndex = 1 # numero de pagina actual
    Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
    resp = SafeGetUrl(Vistas)

    totalFilms = GetTotalFilms(resp)
    line = IndexToLine(DataIndex, totalFilms) # linea de excel en la que estoy escribiendo
    bar = ProgressBar()
    while (DataIndex < totalFilms):

        # we need a parser,Python built-in HTML parser is enough .
        soup = BeautifulSoup(resp.text,'html.parser')
        # Guardo en una lista todas las películas de la página nIndex-ésima
        mylist = soup.findAll("div", {"class": "user-ratings-movie"})

        for i in mylist:
            # La votacion del usuario la leo desde fuera
            # no puedo leer la nota del usuario dentro de la ficha
            UserNote = i.contents[3].contents[1].contents[0]
            SetCellValue(ws, line, 2, int(UserNote))
            SetCellValue(ws, line, 10, str("=B" + str(line) + "+RAND()-0.5"))
            SetCellValue(ws, line, 11, "=(B" + str(line) + "-1)*10/9")
            #guardo la url de la ficha de la pelicula
            url = i.contents[1].contents[1].contents[3].contents[3].contents[0].attrs['href']
            #Entro a la ficha y leo votacion popular, duracion y votantes
            pelicula = Pelicula(urlFA = url)
            pelicula.GetTimeAndFA()
            if (pelicula.duracion != 0):
                # dejo la casilla en blanco si no logra leer ninguna duración de FA
                SetCellValue(ws, line, 4, pelicula.duracion)
            if (pelicula.nota_FA != 0):
                # dejo la casilla en blanco si no logra leer ninguna nota de FA
                SetCellValue(ws, line, 3, pelicula.nota_FA)
                SetCellValue(ws, line, 6, "=ROUND(C" + str(line) + "*2, 0)/2")
                SetCellValue(ws, line, 7, "=B" + str(line) + "-C" + str(line))
                SetCellValue(ws, line, 8, "=ABS(G" + str(line) + ")")
                SetCellValue(ws, line, 9, "=IF($G" + str(line) + ">0,1,0.1)")
                SetCellValue(ws, line, 12, "=(C" + str(line) + "-1)*10/9")
            if (pelicula.votantes_FA != 0):
                # dejo la casilla en blanco si no logra leer ninguna votantes
                SetCellValue(ws, line, 5, pelicula.votantes_FA)
            DataIndex +=1
            # actualizo la barra de progreso
            bar.update(DataIndex/totalFilms)
            # actualizo la linea de escritura en excel
            line = IndexToLine(DataIndex, totalFilms)

        # Siguiente pagina del listado
        nIndex += 1
        Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
        resp = SafeGetUrl(Vistas)


if __name__ == "__main__":
    Ids = {'Sasha': 1230513, 'Jorge': 1742789, 'Guillermo': 4627260, 'Daniel Gallego': 983049, 'Luminador': 7183467,
    'Will_llermo': 565861, 'Roger Peris': 3922745, 'Javi': 247783, 'El Feo': 867335}
    usuario = 'El Feo'
    print("Se van a importar los datos de ", usuario)
    input("Espero Enter...")
    Plantilla = 'Plantilla.xlsx'
    ExcelName = 'Sintaxis - ' + usuario + '.xlsx'
    workbook = load_workbook(Plantilla)
    worksheet = workbook[workbook.sheetnames[0]]
    ReadWatched(Ids[usuario], worksheet)
    workbook.save(ExcelName)
    workbook.close()
