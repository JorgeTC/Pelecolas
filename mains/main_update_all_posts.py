from src.config import manage_config


def main():

    manage_config()

    from src.update_blog import BlogThemeUpdater

    BlogThemeUpdater().update_blog()


if __name__ == "__main__":
    main()
