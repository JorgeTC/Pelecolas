import __init__
from src.essays.google_api import Poster, join
from src.essays import ContentMgr


def main():

    post_data = ContentMgr.get_content()
    Poster.add_post(title=post_data.title,
                    content=post_data.content,
                    labels=post_data.labels)
    join()


if __name__ == '__main__':
    main()
