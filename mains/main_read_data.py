from src.config import manage_config


def main():

    manage_config()

    # Importo los módulos del programa cuando la configuración ya está settada
    from src.usuario import Usuario
    from src.excel import ExcelMgr, Writer

    usuario = Usuario.ask_user()

    ex_doc = ExcelMgr(usuario.nombre)

    writer = Writer(ex_doc.get_worksheet())
    writer.write_watched(usuario.id)

    ex_doc.save_wb()


if __name__ == "__main__":
    main()
