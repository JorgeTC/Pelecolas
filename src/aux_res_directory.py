from pathlib import Path


def get_res_folder(*rel_path: str) -> Path:
    # Carpeta src
    path_file = Path(__file__).parent
    # Carpeta del proyecto
    path_file = path_file.parent
    # Carpeta res
    path_file = path_file / "res"
    # Subdirectorio indicado por el usuario
    path_file = path_file.joinpath(*rel_path)

    return path_file


def get_test_res_folder(*rel_path: str) -> Path:
    # Carpeta src
    path_file = Path(__file__).parent
    # Carpeta del proyecto
    path_file = path_file.parent
    # Carpeta test
    path_file = path_file / "test"
    # Carpeta res
    path_file = path_file / "res"
    # Subdirectorio indicado por el usuario
    path_file = path_file.joinpath(*rel_path)

    return path_file
