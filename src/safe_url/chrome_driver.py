from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service

from src.aux_res_directory import get_res_folder

DRIVER_PATH = get_res_folder("Readdata", "driver", "chromedriver.exe")


def create_chrome_instance() -> Chrome:
    # Abro una instancia de Chrome
    # Lo creo con un conjunto de opciones para no emitir errores por consola
    return webdriver.Chrome(service=Service(DRIVER_PATH),
                            options=get_driver_option())


def get_chrome_instance() -> Chrome:
    try:
        return create_chrome_instance()
    except WebDriverException as driver_error:
        update_chrome_driver()
        driver = create_chrome_instance()
        if not driver:
            print("Por favor, actualiza el driver de Chrome.")
            raise driver_error
        else:
            return driver


def get_driver_option() -> webdriver.ChromeOptions:
    # Opciones para el driver de Chrome
    driver_option = webdriver.ChromeOptions()
    driver_option.headless = True
    driver_option.add_experimental_option('excludeSwitches',
                                          ['enable-logging'])

    return driver_option


def update_chrome_driver():
    import chromedriver_autoinstaller

    # Descargo el nuevo driver
    str_path_new_driver = chromedriver_autoinstaller.install(
        path=DRIVER_PATH.parent)
    # Si no he descargado nada, salgo
    if not str_path_new_driver:
        return

    # Elimino el antiguo driver
    if DRIVER_PATH.is_file():
        DRIVER_PATH.unlink()
    # Coloco el nuevo en la ruta que le corresponde
    path_new_driver = Path(str_path_new_driver)
    path_new_driver.rename(DRIVER_PATH)

    # Elimino la carpeta que ha creado
    dir_new_driver = path_new_driver.parent
    if DRIVER_PATH.parent == dir_new_driver.parent:
        dir_new_driver.rmdir()
