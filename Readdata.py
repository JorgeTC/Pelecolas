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
        now  = datetime.datetime.now()
        left = (1 - done) * (now - self.start) / done
        sec = int(left.total_seconds())
        if sec < 60:
           return "{} seconds".format(sec)
        else:
           return "{} minutes".format(int(sec / 60))

def GetTimeAndFA(url):
    #open with GET method 
    resp=requests.get(url)
    #http_respone 200 means OK status 
    if resp.status_code==200:
        #print("Successfully opened the web page")

         # we need a parser,Python built-in HTML parser is enough . 
        soup=BeautifulSoup(resp.text,'html.parser')


        l=soup.find(id="movie-rat-avg")
        try:
            # guardo la nota de FA en una ficha normal
            dNotaFA = float(l.attrs['content'])
        except:
            # caso en el que no hay nota de FA
            dNotaFA = 0
        
        l=soup.find(itemprop="ratingCount")
        try:
             # guardo la cantidad de votantes en una ficha normal
            nVotantes = l.attrs['content']
            nVotantes = nVotantes.replace('.','')
            nVotantes = int(nVotantes)
        except:
            # caso en el que no hay suficientes votantes
            nVotantes = 0
        
        l=soup.find(id="left-column")
        if ('itemprop' in l.contents[1].contents[11].attrs and l.contents[1].contents[11].attrs['itemprop'] == 'duration'):
            # posicion habitual de la duracion
            duracion = l.contents[1].contents[11].contents[0]
        else:
            # si no está donde debe, lo busco
            duracion = "0"
            for k in l.contents[1].contents:
                # compruebo que k tiene .attrs
                if k != '\n':
                    # compruebo que estoy en un dato y no en una etiqueta
                    if 'itemprop' in k.attrs:
                        if k.attrs['itemprop'] == 'duration':
                            duracion = k.contents[0]
                            break
        # quito el sufijo min.
        duracion = int(duracion.split(' ', 1)[0])

        return dNotaFA, duracion, nVotantes
    
    else:
        # Si ha saltado el capcha, paro el bucle
        PassCaptcha(url)
        return GetTimeAndFA(url)

def PassCaptcha(url):

    webbrowser.open(url)
    resp=requests.get(url)
    print("\nPor favor, entra en FilmAffinity y pasa el capcha por mi.")
    while resp.status_code != 200:
        time.sleep(3)
        resp=requests.get(url)
    return
    
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

def update_progress(progress, timer):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1:.2f}% {2}".format( "="*block + " "*(barLength-block), progress*100, timer.remains(progress))
    sys.stdout.write(text)
    sys.stdout.flush()

def IndexToLine(index, total):
    return total - index + 1


def ReadWatched(IdUser, ws):
    DataIndex = 0 # contador de peliculas
    notaFA = 0.0
    duracion = 0
    nIndex = 1 # numero de pagina actual
    Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
    resp=requests.get(Vistas)
    if resp.status_code!=200:
        PassCaptcha(Vistas)
        resp=requests.get(Vistas)
    totalFilms = GetTotalFilms(resp)
    line = IndexToLine(DataIndex, totalFilms) # linea de excel en la que estoy escribiendo
    timer = Timer()
    while(resp.status_code==200):
        # we need a parser,Python built-in HTML parser is enough . 
        soup=BeautifulSoup(resp.text,'html.parser')

        mylist = soup.find_all('div')

        for i in mylist:
            if(not ('class' in i.attrs)):
                continue
            if(i.attrs['class'][0] != 'user-ratings-movie'):
                continue
            # La votacion del usuario la leo desde fuera
            # no puedo leer la nota del usuario dentro de la ficha
            UserNote = i.contents[3].contents[1].contents[0]
            SetCellValue(ws, line, 2, int(UserNote))            
            SetCellValue(ws, line, 10, str("=B" + str(line) + "+RAND()-0.5"))
            SetCellValue(ws, line, 11, "=(B" + str(line) + "-1)*10/9")
            #guardo la url de la ficha de la pelicula
            url = i.contents[1].contents[1].contents[3].contents[3].contents[0].attrs['href']
            #Entro a la ficha y leo votacion popular, duracion y votantes
            notaFA, duracion, votantes = GetTimeAndFA(url)
            if (duracion != 0):
                # dejo la casilla en blanco si no logra leer ninguna duración de FA
                SetCellValue(ws, line, 4, duracion)
            if (notaFA != 0):
                # dejo la casilla en blanco si no logra leer ninguna nota de FA
                SetCellValue(ws, line, 3, notaFA)
                SetCellValue(ws, line, 6, "=ROUND(C" + str(line) + "*2, 0)/2")
                SetCellValue(ws, line, 7, "=B" + str(line) + "-C" + str(line))
                SetCellValue(ws, line, 8, "=ABS(G" + str(line) + ")")
                SetCellValue(ws, line, 9, "=IF($G" + str(line) + ">0,1,0.1)")
                SetCellValue(ws, line, 12, "=(C" + str(line) + "-1)*10/9")
            if (votantes != 0):
                # dejo la casilla en blanco si no logra leer ninguna votantes
                SetCellValue(ws, line, 5, votantes)
            DataIndex +=1
            # actualizo la barra de progreso
            update_progress(DataIndex/totalFilms, timer)
            # actualizo la linea de escritura en excel
            line = IndexToLine(DataIndex, totalFilms)
            
        # Siguiente pagina del listado
        nIndex += 1
        Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
        resp=requests.get(Vistas)


if __name__ == "__main__":
    Ids = {'Sasha': 1230513, 'Jorge': 1742789, 'Guillermo': 4627260, 'Daniel Gallego': 983049, 'Luminador': 7183467,
    'Will_llermo': 565861, 'Roger Peris': 3922745}
    usuario = 'Guillermo'
    print("Se van a importar los datos de ", usuario)
    input("Espero Enter...")
    Plantilla = 'Plantilla.xlsx'
    ExcelName = 'Sintaxis - ' + usuario + '.xlsx'
    workbook = load_workbook(Plantilla)
    worksheet = workbook[workbook.sheetnames[0]]
    ReadWatched(Ids[usuario], worksheet)
    workbook.save(ExcelName)
    workbook.close()