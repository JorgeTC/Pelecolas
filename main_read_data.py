from .Usuario import Usuario
from .ExcelMgr import ExcelMgr
from .Writer import Writer
from .dlg_config import manage_config


def main():

    manage_config()

    usuario = Usuario()

    ex_doc = ExcelMgr(usuario.nombre)

    writer = Writer(usuario.id, ex_doc.get_worksheet())
    writer.read_watched()

    ex_doc.save_wb()

if __name__ == "__main__":
    main()
