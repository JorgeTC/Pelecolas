import inspect
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Generic, Iterator, TypeVar
from unittest import mock
from unittest.mock import MagicMock

from src.config import Config, Param, Section


def import_path(function: Callable) -> str:
    # Compongo la ruta de importación
    function_path = function.__qualname__
    definition_path = Path(inspect.getfile(function))
    definition_path = definition_path.with_suffix("")
    src_path = next(parent for parent in definition_path.parents
                    if parent.name == 'src')
    relative_definition = definition_path.relative_to(src_path.parent)
    return ".".join((*relative_definition.parts, function_path))


@contextmanager
def mock_without_replace(to_mock: Callable) -> Iterator[mock.MagicMock]:

    # Compongo la ruta de importación
    function_path = import_path(to_mock)

    # Devuelvo la función con su implementación
    with mock.patch(function_path, side_effect=to_mock) as function_mock:
        yield function_mock


@contextmanager
def mock_config(config_fn: Callable, section: Section, param: Param, value) -> Iterator[mock.MagicMock]:

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
def mock_config_get_bool(section: Section, param: Param, value: bool) -> Iterator[mock.MagicMock]:
    with mock_config(Config.get_bool, section, param, value) as mock_fn:
        yield mock_fn


@contextmanager
def mock_config_get_value(section: Section, param: Param, value: bool) -> Iterator[mock.MagicMock]:
    with mock_config(Config.get_value, section, param, value) as mock_fn:
        yield mock_fn


MockReturn = TypeVar('MockReturn')


class NonSubstitutionFunctionMock(MagicMock, Generic[MockReturn]):
    def __new__(cls, mock: MagicMock, return_values: list[MockReturn]) -> 'NonSubstitutionFunctionMock':
        # Modifico el objeto y lo devuelvo
        cls.__init__(mock, return_values)
        return mock

    def __init__(self, return_values: list[MockReturn]):
        self.return_values = return_values


class MockFunctionWithoutReplace(Generic[MockReturn]):
    def __init__(self, to_mock: Callable[..., MockReturn]):
        # Compongo la ruta de importación
        self.function_path = import_path(to_mock)

        self.return_values: list[MockReturn] = []

        def side_effect(*args, **kwargs) -> MockReturn:
            value = to_mock(*args, **kwargs)
            self.return_values.append(value)
            return value

        self.patch = mock.patch(self.function_path, side_effect=side_effect)

    def __enter__(self) -> NonSubstitutionFunctionMock[MockReturn]:
        function_mock = self.patch.__enter__()
        return NonSubstitutionFunctionMock(function_mock,
                                           self.return_values)

    def __exit__(self, *exec_info):
        self.patch.__exit__(*exec_info)


class NonSubstitutionGeneratorMock(MagicMock, Generic[MockReturn]):
    def __new__(cls, mock: MagicMock, return_values: list[list[MockReturn]]) -> 'NonSubstitutionGeneratorMock':
        # Modifico el objeto y lo devuelvo
        cls.__init__(mock, return_values)
        return mock

    def __init__(self, return_values: list[list[MockReturn]]):
        self.return_values = return_values


class MockGeneratorWithoutReplace(Generic[MockReturn]):
    def __init__(self, to_mock: Callable[..., Iterator[MockReturn]]):

        # Compongo la ruta de importación
        self.function_path = import_path(to_mock)

        self.return_values: list[list[MockReturn]] = []

        def side_effect(*args, **kwargs) -> Iterator[MockReturn]:
            self.return_values.append([])
            for value in to_mock(*args, **kwargs):
                self.return_values[-1].append(value)
                yield value

        self.patch = mock.patch(self.function_path, side_effect=side_effect)

    def __enter__(self) -> NonSubstitutionGeneratorMock[MockReturn]:
        function_mock = self.patch.__enter__()
        return NonSubstitutionGeneratorMock(function_mock,
                                            self.return_values)

    def __exit__(self, *exec_info):
        self.patch.__exit__(*exec_info)
