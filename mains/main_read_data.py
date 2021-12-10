from src.dlg_config import manage_config


def main(path):

    manage_config()

    # Importo los módulos del programa cuando la configuración ya está settada
    from src.Usuario import Usuario
    from src.ExcelMgr import ExcelMgr
    from src.Writer import Writer
    usuario = Usuario()

    ex_doc = ExcelMgr(usuario.nombre)

    writer = Writer(usuario.id, ex_doc.get_worksheet())
    writer.read_watched()

    ex_doc.save_wb(path)

if __name__ == "__main__":
    main()