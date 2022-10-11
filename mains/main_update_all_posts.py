from src.config import manage_config


def main():

    manage_config()

    import src.update_blog as UpdateBlog

    UpdateBlog.update_blog()


if __name__ == "__main__":
    main()
