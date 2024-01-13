import __init__
from src.essays.word import WordReader


def print_columns(to_print: list[tuple[str, ...]], separation=1):
    # Find the maximum width for each column
    column_widths = [max(len(str(item)) for item in column) + separation
                     for column in zip(*to_print)]

    # Print the data
    for row in to_print:
        for width, column in zip(column_widths, row):
            print(f"{column:{width}}", end="")
        print()


def print_count_per_year():
    count_each_year = WordReader.count_each_year()

    # First rows with count for each year
    years = [(f"{year}:", f"{films_in_year}")
             for year, films_in_year in count_each_year.items()]
    all_data = years + [("Total:", f"{len(WordReader.TITULOS)}")]

    print_columns(all_data)


def main():

    WordReader.list_titles()
    WordReader.write_list()

    print_count_per_year()
    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
