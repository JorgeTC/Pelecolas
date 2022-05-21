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

    ex_doc = ExcelMgr("Sample")

    writer = Writer(ex_doc.get_worksheet())
    writer.read_sample(1_000)

    ex_doc.save_wb()

if __name__ == "__main__":
    main()