from functools import wraps
from threading import Thread
from typing import Callable, Generic, TypeVar

StoredValue = TypeVar('StoredValue')


class AsyncInitializer(Generic[StoredValue]):

    def __init__(self, initializer: Callable[[], StoredValue]):
        # Variable lenta de calcular y cuya inicialización se arranca en este constructor
        self.value: StoredValue | None = None
        # Función que inicializará el objeto que necesito
        self.initializer = initializer

        # Guardo el hilo que está realizando la inicialización para
        # poder esperar a que termine su ejecución antes de devolver el valor.
        # Daemon porque no quiero que el cierre del programa espere a que termine la inicialización:
        # si estoy cerrando el programa ya no necesito el valor que está calculando
        self.init_thread = Thread(target=self.initialize,
                                  name=self.initializer.__name__,
                                  daemon=True)
        # Inicio la ejecución
        self.init_thread.start()

        # Atributo para guardar las excepciones que surjan durante la inicialización.
        # No quiero que salten en el hilo de inicialización, sino cuando se me solicite el resultado.
        self.exception: Exception | None = None

    def initialize(self):
        try:
            self.value = self.initializer()
        except Exception as e:
            # Guardo la excepción. No la lanzo ahora, la lanzaré cuando se me pida el valor
            self.exception = e

    def get(self) -> StoredValue:
        # Antes de devolver nada, espero a que termine la inicialización
        self.init_thread.join()

        # Si la inicialización ha ido mal, no devuelvo el valor: lanzo la excepción
        if self.exception:
            raise self.exception

        # La variable ha sido inicializada: la devuelvo
        return self.value


def async_initializer(func: Callable[[], StoredValue]) -> Callable[[], StoredValue]:

    # Al llamar a este constructor se va a crear un hilo que ejecutará func.
    # Eso significa que todas las funciones de las que depende func deben estar definidas antes que func
    initializer = AsyncInitializer(func)

    @wraps(func)
    def wrapper() -> StoredValue:
        return initializer.get()

    return wrapper
