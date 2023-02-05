import __init__
from src.config import Config, Param, Section
from src.scrap_fa import ExcelMgr, Writer


def main():

    ex_doc = ExcelMgr(Config.get_value(Section.READDATA, Param.SAMPLE_OUTPUT))

    writer = Writer(ex_doc.get_worksheet())
    sample_size = int(input("Introduzca el tamaño de la muestra buscada "))
    writer.write_sample(sample_size)

    ex_doc.save_wb()


if __name__ == "__main__":
    main()
