from src.config import manage_config


def main():

    manage_config()

    import src.update_blog as UpdateBlog

    post = UpdateBlog.select_post_to_update()
    UpdateBlog.update_post(post)


if __name__ == "__main__":
    main()
