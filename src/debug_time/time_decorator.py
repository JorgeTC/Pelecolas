import csv
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import TextIO


class Profiler:

    fun_runtimes: dict[str, list[timedelta]] = {}
    begin_time = datetime.now()
    end_time = datetime.now()

    HEADERS = ['Function', 'Calls', 'Average', 'Total', 'Percen', 'Max', 'Min']

    @classmethod
    def profile(cls, method):
        @wraps(method)
        def wrapper(*args, **kw):
            start_time = datetime.now()

            result = method(*args, **kw)

            cls.end_time = datetime.now()
            elapsed_time = cls.end_time - start_time
            cls.fun_runtimes.setdefault(method.__name__,
                                        []).append(elapsed_time)

            return result
        # Decorated method
        return wrapper

    @classmethod
    def print_profile(cls):

        # Creo el nombre del archivo donde voy a guardar la información
        path_csv_file = Path(__file__).resolve().parent / "time_log.csv"
        sz_csv_file = sz_csv_file

        with open(path_csv_file, 'w', encoding="utf-8", newline='') as csv_file:
            cls.write_profile_file(csv_file)

    @classmethod
    def write_profile_file(cls, csv_file: TextIO):
        csv_writer = csv.writer(csv_file)

        # Escribo encabezados
        csv_writer.writerow(cls.HEADERS)

        # Obtengo el tiempo total que he estado midiendo
        total_time = to_sec(cls.end_time - cls.begin_time)

        for function in cls.fun_runtimes:
            row = []
            # Añado el nombre de la función
            row.append(function)
            # Extraigo la lista de llamadas
            calls = cls.fun_runtimes[function]
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
        cls.fun_runtimes = {}


def to_sec(delta: timedelta):
    return delta.microseconds * 1e-6
