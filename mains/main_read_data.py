import __init__
from src.excel import ExcelMgr, Writer
from src.usuario import Usuario


def main():

    usuario = Usuario.ask_user()

    ex_doc = ExcelMgr(usuario.nombre)

    writer = Writer(ex_doc.get_worksheet())
    writer.write_watched(usuario.id)

    ex_doc.save_wb()


if __name__ == "__main__":
    main()
