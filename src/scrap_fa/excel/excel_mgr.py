import logging

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from src.aux_res_directory import get_res_folder
from src.config import Config, Param, Section


class ExcelMgr:

    OUTPUT_FILE_NAME = 'Sintaxis - {}.xlsx'.format
    TEMPLATE_NAME = 'Plantilla.xlsx'

    def __init__(self, user: str):
        # Abro la carpeta donde está la plantilla
        template_path = get_res_folder("Readdata", self.TEMPLATE_NAME)

        # Abro el archivo excel
        self.wb = load_workbook(template_path)
        # Abro la primera de las hojas, es la única en la que escribo
        self.ws: Worksheet = self.wb.worksheets[0]

        # Construyo el nombre con el que voy a guardar el excel
        self.excel_name = self.OUTPUT_FILE_NAME(user)

        # Cargo la carpeta donde se guardará
        self.output_dir_path = Config.get_folder_path(Section.READDATA, Param.OUTPUT_EXCEL)

    def get_worksheet(self) -> Worksheet:
        return self.ws

    def save_wb(self):
        excel_path = self.output_dir_path / self.excel_name
        logging.debug(f"Saving excel file: {excel_path}")
        # Me han pasado la carpeta de destino como argumento
        self.wb.save(excel_path)
        # Cierro el archivo excel
        self.wb.close()
