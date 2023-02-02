import __init__
import src.essays.update_blog as UpdateBlog


def main():

    post = UpdateBlog.select_post_to_update()
    UpdateBlog.update_post(post)


if __name__ == "__main__":
    main()
