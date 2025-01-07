import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import current_thread

import requests

import __init__
import src.gui as GUI
from src.essays.searcher import Searcher
from src.pelicula import Pelicula

seen_films = [
    "Con quién viajas",
    "El pirata (1948)",
    "Cría cuervos…",
    "Alice (1988)",
    "El pisito",
    "El mundo sigue",
    "Poliamor para principiantes",
    "Un condenado a muerte se ha escapado",
    "Titane",
    "Drive my car",
    "La torre de los siete jorobados",
    "Vinieron de dentro de…",
    "La hora del lobo",
    "La parada de los monstruos",
    "El fantasma de la sauna",
    "Días extraños",
    "Los siete samuráis",
    "Lejos de Praga",
    "Hana y Alice (2004)",
    "Hasta el último hombre",
    "Masacre. Ven y mira",
    "Te doy mis ojos",
    "La prima Angélica",
    "El autoestopista",
    "Red",
    "Espartaco (1960)",
    "Cryptozoo",
    "Antoñito vuelve a casa",
    "Soul",
    "De aquí a la eternidad",
    "Camera café, la película",
    "Bienvenidos a Belleville",
    "La tienda en la Calle Mayor",
    "El monosabio",
    "Arrebato (1979)",
    "Laura",
    "El poder del perro",
    "El hombre del Norte",
    "Compartimento no 6",
    "Veneciafrenia",
    "Satyricon",
    "El apartamento",
    "Mamá o papá (2021)",
    "Memoria",
    "¡Dolores, guapa!",
    "La verbena de la Paloma (1935)",
    "Abajo los hombres",
    "El desencanto",
    "Todo a la vez en todas partes",
    "Uno para todos",
    "Vértigo (de entre los muertos)",
    "Men",
    "Mi tío Jacinto",
    "Cuando fuimos brujas",
    "La ventana indiscreta",
    "Honor de cavalleria",
    "Pacifiction",
    "La Chinoise",
    "Modelo 77",
    "El crítico (2022)",
    "La estanquera de Vallecas",
    "La pasión de Juana de Arco",
    "La muerte cansada",
    "Mad God",
    "Repulsión",
    "La semilla del diablo",
    "El incinerador de cadáveres",
    "La Lola se va a los puertos (1947)",
    "Rojo y negro (1942)",
    "As bestas",
    "Más allá de los dos minutos infinitos",
    "El infierno del odio",
    "El portero de noche",
    "Terror en Dunwich",
    "Mantícora",
    "It’s such a beautiful day (2012)",
    "Eo"
]

SZ_INVALID_CHAR = "\/:*?<>|"
DEST_FOLDER = Path("/home/jorge/Documents/Reseñas/2024pictures")


def main():
    print(len(seen_films))

    with ThreadPoolExecutor() as executor:
        executor.map(download_picture, seen_films)

    GUI.join_GUI()


def download_picture(title: str):
    # Cambio necesario para poder usar la GUI con varios hilos
    current_thread().name = title

    film = Pelicula.from_fa_url(get_url(title))
    film.get_image_url()
    res = requests.get(film.url_image, stream=True)
    title = "".join(i for i in str(title)
                    if i not in SZ_INVALID_CHAR)
    with open(DEST_FOLDER / f"{title}.jpg", 'wb') as f:
        shutil.copyfileobj(res.raw, f)
    GUI.GUI.close_suite()


def get_url(title: str) -> str:
    if not (url := Searcher(title).get_url()):
        url = GUI.Input(f"Introduce la url de {title}: ")
    return url


if __name__ == '__main__':
    main()
