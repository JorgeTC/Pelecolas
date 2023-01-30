import pytest

from src.aux_res_directory import get_test_res_folder
from src.blog_csv_mgr import BlogCsvMgr
from src.html.dlg_make_html import filter_list_from_csv


@pytest.fixture
def csv_list() -> list[list[str]]:
    return BlogCsvMgr.open_to_read(get_test_res_folder('csv_test.csv'))


@pytest.fixture
def title_list() -> list[str]:
    return ["La caza (1966)",
            "Men",
            "1917",
            "Miedo (1917)",
            "La caza (2012)",
            "¡Dolores, guapa!",
            "La caza"]


def test_filter(title_list: list[str], csv_list: list[list[str]]):
    filtered_list = filter_list_from_csv(title_list, csv_list)

    # No se elimine si el año no coincide con el del csv
    assert "La caza (1966)" in filtered_list
    # No se elimine si no está en el csv
    assert "Men" in filtered_list
    # Se distinga un año en el título de un año de película
    assert "1917" not in filtered_list
    assert "Miedo (1917)" in filtered_list
    # Se elimina si el año coincide
    assert "La caza (2012)" not in filtered_list
    # No dan problema las comillas alrededor del título
    assert "¡Dolores, guapa!" not in filtered_list
    # No está indicado el año: se elimina
    assert "La caza" not in filtered_list
