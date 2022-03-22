from src.dlg_config import manage_config


def main(path):

    manage_config()

    from src.blog_theme_updater import BlogThemeUpdater

    BlogThemeUpdater().update_blog()


if __name__ == "__main__":
    main()
