import inspect
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator
from unittest import mock
from src.config import Config, Param, Section


def import_path(function: Callable) -> str:
    # Compongo la ruta de importación
    function_path = function.__qualname__
    definition_path = Path(inspect.getfile(function))
    while definition_path.stem != 'src':
        function_path = definition_path.stem + "." + function_path
        definition_path = definition_path.parent
    function_path = "src." + function_path
    return function_path


@contextmanager
def mock_without_replace(to_mock: Callable) -> Iterator[mock.MagicMock]:

    # Compongo la ruta de importación
    function_path = import_path(to_mock)

    # Devuelvo la función con su implementación
    with mock.patch(function_path, side_effect=to_mock) as function_mock:
        yield function_mock


@contextmanager
def mock_config(config_fn: Callable, section: Section, param: Param, value):

    # Compongo la ruta de importación
    function_path = import_path(config_fn)

    def side_effect(arg_section: Section, arg_param: Param):
        if arg_section == section and arg_param == param:
            return value
        return config_fn(arg_section, arg_param)

    # Devuelvo la función con su implementación
    with mock.patch(function_path, side_effect=side_effect) as mock_fn:
        yield mock_fn


@contextmanager
def mock_config_get_bool(section: Section, param: Param, value: bool):
    with mock_config(Config.get_bool, section, param, value) as mock_fn:
        yield mock_fn


@contextmanager
def mock_config_get_value(section: Section, param: Param, value: bool):
    with mock_config(Config.get_value, section, param, value) as mock_fn:
        yield mock_fn
