from selenium.webdriver import Firefox, FirefoxOptions


def get_firefox_instance() -> Firefox:
    # Abro una instancia de Firefox
    # Lo creo con un conjunto de opciones para no emitir errores por consola
    return Firefox(get_driver_options())


def get_driver_options() -> FirefoxOptions:
    # Opciones para el driver de Chrome
    driver_option = FirefoxOptions()
    driver_option.headless = True

    return driver_option
