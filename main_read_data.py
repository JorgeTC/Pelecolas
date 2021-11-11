from .dlg_config import manage_config


def main():

    manage_config()

    # Importo los módulos del programa cuando la configuración ya está settada
    from .Usuario import Usuario
    from .ExcelMgr import ExcelMgr
    from .Writer import Writer
    usuario = Usuario()

    ex_doc = ExcelMgr(usuario.nombre)

    writer = Writer(usuario.id, ex_doc.get_worksheet())
    writer.read_watched()

    ex_doc.save_wb()

if __name__ == "__main__":
    main()
