import test.mocks_word_folder as mocks_w

from src.aux_res_directory import get_test_res_folder
from src.essays.word.word_reader import WordReader


all_titles = ["Película 1",
              "Película 2",
              "Tan triste como ella (1963)",
              "Don de la ebriedad",
              "Película 100"]


def test_read_all_titles():
    name_folder = get_test_res_folder("word", "test_word")
    with mocks_w.set_word_folder(name_folder):
        assert len(WordReader.TITULOS) == len(all_titles)
        for title_key, ref_title in zip(WordReader.TITULOS.keys(), all_titles):
            assert title_key == ref_title


def test_ask_year():
    name_folder = get_test_res_folder("word", "test_word")
    with mocks_w.set_word_folder(name_folder):
        assert WordReader.find_year("Película 1") == 2018
        assert WordReader.find_year("Película 2") == 2018
        assert WordReader.find_year("Tan triste como ella (1963)") == 2018
        assert WordReader.find_year("Don de la ebriedad") == 2019
        assert WordReader.find_year("Película 100") == 2019


def test_count_each_year():
    name_folder = get_test_res_folder("word", "test_word")
    with mocks_w.set_word_folder(name_folder):
        count_dict = WordReader.count_each_year()
        assert count_dict == {2018: 3, 2019: 2}
        assert sum(count_dict.values()) == len(all_titles)
