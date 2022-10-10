from src.config import manage_config


def main():

    manage_config()

    from src.update_blog import BlogThemeUpdater

    BlogThemeUpdater().select_and_update_post()


if __name__ == "__main__":
    main()
