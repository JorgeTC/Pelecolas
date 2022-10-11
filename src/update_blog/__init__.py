from src.google_api import Post, join
from src.update_blog.blog_theme_updater import (BlogThemeUpdater,
                                                PostThemeUpdater,
                                                exist_repeated_posts)

exist_repeated_posts()


def select_post_to_update() -> Post:
    return PostThemeUpdater.select_post_to_update()


def update_post(post: Post):
    PostThemeUpdater.update_post(post)
    join()


def update_blog():
    BlogThemeUpdater.update_blog()
    join()


__all__ = [select_post_to_update, update_post, update_blog]
