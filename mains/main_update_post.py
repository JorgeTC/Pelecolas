import __init__
import src.essays.update_blog as UpdateBlog


def main():
    try:
        post = UpdateBlog.select_post_to_update()
    except KeyboardInterrupt:
        return
    UpdateBlog.update_post(post)


if __name__ == "__main__":
    main()
