from concurrent.futures import Future
from threading import Thread
from typing import Callable, Generic, TypeVar
import logging

StoredValue = TypeVar('StoredValue')


class AsyncInitializer(Generic[StoredValue]):

    def __init__(self, initializer: Callable[[], StoredValue]):
        # Variable lenta de calcular y cuya inicialización se arranca en este constructor
        # El futuro guardará el estado final de la inicialización: valor o excepción
        # La excepción se lanzare cuando se acceda al valor, no durante la inicialización
        self._future: Future[StoredValue] = Future()
        # Función que inicializará el objeto que necesito
        self.initializer = initializer

        # Guardo el hilo que está realizando la inicialización para
        # poder esperar a que termine su ejecución antes de devolver el valor.
        # Daemon porque no quiero que el cierre del programa espere a que termine la inicialización:
        # si estoy cerrando el programa ya no necesito el valor que está calculando
        self.init_thread = Thread(target=self.initialize,
                                  name=getattr(self.initializer, "__name__", repr(self.initializer)),
                                  daemon=True)
        logging.debug(f"Starting async initialization in thread {self.init_thread.name}")
        # Inicio la ejecución
        self.init_thread.start()

    def initialize(self):
        try:
            self._future.set_result(self.initializer())
            logging.debug(f"Finalized async initialization in thread {self.init_thread.name}")
        except Exception as e:
            logging.debug(f"Exception caught in thread {self.init_thread.name}: {e}")
            # Guardo la excepción. No la lanzo ahora, la lanzaré cuando se me pida el valor
            self._future.set_exception(e)

    def get(self) -> StoredValue:
        # Acceso al resultado.
        # Si ha habido una excepción, se lanzará en este momento
        return self._future.result()
