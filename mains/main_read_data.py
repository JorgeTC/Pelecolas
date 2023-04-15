import __init__
from src.scrap_fa import ExcelMgr, UserFA, Writer


def main():

    user = UserFA.ask_user()

    ex_doc = ExcelMgr(user.name)

    writer = Writer(ex_doc.get_worksheet())
    writer.write_watched(user.id)

    ex_doc.save_wb()


if __name__ == "__main__":
    main()
