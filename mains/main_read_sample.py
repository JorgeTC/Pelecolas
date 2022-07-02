import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CODE_DIR = SCRIPT_DIR.parent
sys.path.append(str(CODE_DIR))

from src.config import manage_config


def main():

    manage_config()

    # Importo los módulos del programa cuando la configuración ya está settada
    from src.excel_mgr import ExcelMgr
    from src.writer import Writer

    ex_doc = ExcelMgr(Config.get_value(Section.READDATA, Param.SAMPLE_OUTPUT))

    writer = Writer(ex_doc.get_worksheet())
    sample_size = int(input("Introduzca el tamaño de la muestra buscada "))
    writer.write_sample(sample_size)

    ex_doc.save_wb()

if __name__ == "__main__":
    main()