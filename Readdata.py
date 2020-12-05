from os import waitpid
from numpy.lib.function_base import append
import requests
import xlsxwriter as xlsx
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver

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
                    # compruebo que estoy en un dato y uno en una etiqueta
                    if 'itemprop' in k.attrs:
                        if k.attrs['itemprop'] == 'duration':
                            duracion = k.contents[0]
                            break
        # quito el sufijo min.
        duracion = int(duracion.split(' ', 1)[0])

        return dNotaFA, duracion, nVotantes
    
    else:
        # Si ha saltado el capcha, paro el bucle
        PassCaptcha()
        return GetTimeAndFA(url)

def PassCaptcha():
    time.sleep(0.5)
    print("\nPor favor, entra en FilmAffinity y pasa el capcha por mi.")
    input("Espero Enter...")
    return

def PassCaptchaAutomatic(url):
    driver = webdriver.Chrome()
    # Go to your page url
    driver.get(url)
    # Get button you are going to click by its id ( also you could us find_element_by_css_selector to get element by css selector)
    button_element = driver.find_element_by_class_name("content")
    button_element = button_element.find_element_by_class_name("captcha")
    button_element = button_element.find_element_by_class_name("g-recaptcha")
    button_element.click()
    time.sleep(1)
    button_element = driver.find_element_by_xpath("/html/body/div[1]/div[2]/form[1]/div[3]")
    button_element.click()
    driver.close()

    resp=requests.get(url)
    #http_respone 200 means OK status 
    return resp.status_code==200

def GetTotalFilms(resp):
    soup=BeautifulSoup(resp.text,'html.parser')
    # me espero que haya un único "value-box active-tab"
    mydivs = soup.find("a", {"class": "value-box active-tab"})
    stringNumber = mydivs.contents[3].contents[1]
    # Elimino el punto de los millares
    stringNumber = stringNumber.replace('.','')
    return int(stringNumber)

def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    elif progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1:.2f}% {2}".format( "="*block + " "*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def IndexToLine(index, total):
    
    return total - index - 1


def ReadWatched(IdUser, ws):
    DataIndex = 0 # contador de peliculas
    notaFA = 0.0
    duracion = 0
    nIndex = 1 # numero de pagina actual
    Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
    resp=requests.get(Vistas)
    if resp.status_code!=200:
        PassCaptcha()
    totalFilms = GetTotalFilms(resp)
    line = IndexToLine(DataIndex, totalFilms) # linea de excel en la que estoy escribiendo
    while(resp.status_code==200):
        # we need a parser,Python built-in HTML parser is enough . 
        soup=BeautifulSoup(resp.text,'html.parser')

        mylistAux = soup.find_all('div')
        mylist = []
        for i in mylistAux:
            if('class' in i.attrs):
                if(i.attrs['class'][0] == 'user-ratings-movie'):
                    mylist.append(i)
        mylistAux.clear()

        for i in mylist:
            # La votacion del usuario la leo desde fuera
            # no puedo leer la nota del usuario dentro de la ficha
            UserNote = i.contents[3].contents[1].contents[0]
            ws.write(line, 0, int(UserNote)) # excel
            #guardo la url de la ficha de la pelicula
            url = i.contents[1].contents[1].contents[3].contents[3].contents[0].attrs['href']
            #Entro a la ficha y leo votacion popular, duracion y votantes
            notaFA, duracion, votantes = GetTimeAndFA(url)
            if (duracion != 0):
                # dejo la casilla en blanco si no logra leer ninguna duración de FA
                ws.write(line, 3, duracion) # excel
            if (notaFA != 0):
                # dejo la casilla en blanco si no logra leer ninguna nota de FA
                ws.write(line, 1, notaFA) # excel
            if (votantes != 0):
                # dejo la casilla en blanco si no logra leer ninguna votantes
                ws.write(line, 4, votantes) # excel
            DataIndex +=1
            # actualizo la barra de progreso
            update_progress(DataIndex/totalFilms)
            # actualizo la linea de escritura en excel
            line = IndexToLine(DataIndex, totalFilms)



        # Siguiente pagina del listado
        nIndex += 1
        Vistas = 'https://www.filmaffinity.com/es/userratings.php?user_id=' + str(IdUser) + '&p=' + str(nIndex) + '&orderby=4'
        resp=requests.get(Vistas)
    if(DataIndex < totalFilms):
        ws.write(0, 5, "nIndex")
        ws.write(0, 6, nIndex)
        print("Error %d peliculas importadas", DataIndex )

def main():
    Ids = {'Sasha': 1230513, 'Jorge': 1742789, 'Guillermo': 4627260, 'Daniel Gallego': 983049, 'Luminador': 7183467,
    'Will_llermo': 565861}
    usuario = 'Will_llermo'
    print("Se van a importar los datos de ", usuario)
    input("Espero Enter...")
    ExcelName = 'demo_' + usuario + '.xlsx'
    workbook = xlsx.Workbook(ExcelName)
    worksheet = workbook.add_worksheet()
    ReadWatched(Ids[usuario], worksheet)
    workbook.close()
    return True


if __name__ == "__main__":
    main()