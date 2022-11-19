import csv
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path


class Profiler:

    fun_runtimes: dict[str, list[timedelta]] = {}
    begin_time = datetime.now()
    end_time = datetime.now()

    HEADERS = ['Function', 'Calls', 'Average', 'Total', 'Percen', 'Max', 'Min']

    @classmethod
    def profile(self, method):
        @wraps(method)
        def wrapper(*args, **kw):
            start_time = datetime.now()

            result = method(*args, **kw)

            self.end_time = datetime.now()
            elapsed_time = self.end_time - start_time
            self.fun_runtimes.setdefault(method.__name__, []).append(elapsed_time)

            return result
        # Decorated method
        return wrapper

    @classmethod
    def print_profile(self):

        # Creo el nombre del archivo donde voy a guardar la información
        sz_csv_file = Path(__file__).resolve().parent
        sz_csv_file = sz_csv_file / "time_log.csv"

        self.csv_file = open(sz_csv_file, 'w',
                             encoding="utf-8", newline='')
        csv_writer = csv.writer(self.csv_file)

        # Escribo encabezados
        csv_writer.writerow(self.HEADERS)

        # Obtengo el tiempo total que he estado midiendo
        total_time = to_sec(self.end_time - self.begin_time)

        for function in self.fun_runtimes:
            row = []
            # Añado el nombre de la función
            row.append(function)
            # Extraigo la lista de llamadas
            calls = self.fun_runtimes[function]
            calls = [to_sec(i) for i in calls]
            # Añado el número de llamadas
            row.append(len(calls))
            # Añado la media de tiempo en cada llamada
            row.append(sum(calls) / len(calls))
            # Añado el tiempo total
            all_calls = sum(calls)
            row.append(all_calls)
            # Añado el porcentaje de tiempo que ha consumido
            row.append(f'{all_calls/total_time} %')
            # Añado el máximo
            row.append(max(calls))
            # Añado el mínimo
            row.append(min(calls))

            csv_writer.writerow(row)

        # Limpio el objeto de registro
        self.fun_runtimes = {}


def to_sec(delta: timedelta):
    return delta.microseconds * 1e-6
