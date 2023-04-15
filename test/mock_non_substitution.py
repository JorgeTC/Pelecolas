import inspect
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar
from unittest import mock
from unittest.mock import MagicMock


def import_path(function: Callable) -> str:
    # Compongo la ruta de importación
    function_path = function.__name__
    definition_path = Path(inspect.getfile(function))
    while definition_path.stem != 'src':
        function_path = definition_path.stem + "." + function_path
        definition_path = definition_path.parent
    function_path = "src." + function_path
    return function_path


MockReturn = TypeVar('MockReturn')


class NonSubstitutionFunctionMock(MagicMock):
    def __new__(cls, mock: MagicMock, return_values: list[MockReturn]) -> 'NonSubstitutionFunctionMock':
        # Modifico el objeto y lo devuelvo
        cls.__init__(mock, return_values)
        return mock

    def __init__(self, return_values: list[MockReturn]):
        self.return_values = return_values


@contextmanager
def mock_function_without_replace(to_mock: Callable[[Any], MockReturn]) -> Iterator[NonSubstitutionFunctionMock]:

    # Compongo la ruta de importación
    function_path = import_path(to_mock)

    return_values: list[MockReturn] = []
    def side_effect(*args, **kwargs) -> MockReturn:
        value = to_mock(*args, **kwargs)
        return_values.append(value)
        return value

    # Devuelvo la función con su implementación
    with mock.patch(function_path, side_effect=side_effect) as function_mock:
        yield NonSubstitutionFunctionMock(function_mock, return_values)


class NonSubstitutionGeneratorMock(MagicMock):
    def __new__(cls, mock: MagicMock, return_values: list[list[MockReturn]]) -> 'NonSubstitutionGeneratorMock':
        # Modifico el objeto y lo devuelvo
        cls.__init__(mock, return_values)
        return mock

    def __init__(self, return_values: list[list[MockReturn]]):
        self.return_values = return_values


@contextmanager
def mock_generator_without_replace(to_mock: Callable[[Any], Iterator[MockReturn]]) -> Iterator[NonSubstitutionGeneratorMock]:

    # Compongo la ruta de importación
    function_path = import_path(to_mock)

    return_values: list[list[MockReturn]] = []
    def side_effect(*args, **kwargs) -> MockReturn:
        return_values.append([])
        for value in to_mock(*args, **kwargs):
            return_values[-1].append(value)
            yield value

    # Devuelvo la función con su implementación
    with mock.patch(function_path, side_effect=side_effect) as function_mock:
        yield NonSubstitutionGeneratorMock(function_mock, return_values)
