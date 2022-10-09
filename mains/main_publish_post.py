from src.config import manage_config


def main():

    manage_config()

    from src.google_api import Poster
    from src.content_mgr import ContentMgr

    post_data = ContentMgr.get_content()
    Poster.add_post(title=post_data.title,
                    content=post_data.content,
                    labels=post_data.labels)


if __name__ == '__main__':
    main()
