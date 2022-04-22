from src.dlg_config import manage_config


def main():

    manage_config()

    from src.blog_theme_updater import BlogThemeUpdater

    BlogThemeUpdater().select_and_update_post()


if __name__ == "__main__":
    main()
