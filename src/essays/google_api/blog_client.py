from dataclasses import asdict
from enum import Enum
from typing import Any

from googleapiclient.discovery import Resource

from src.config import Config, Param, Section

from ..async_initializer import async_initializer
from .api_dataclasses import Blog, Post
from .google_api_mgr import GoogleService, get_google_service
from .google_client import GoogleClient

BLOG_ID = Config.get_value(Section.POST, Param.BLOG_ID)


def get_blogs_of_user() -> list[dict[str, Any]]:
    blogs = get_blogs()
    list_operation = blogs.listByUser(userId='self')
    return GoogleClient.execute_and_wait(list_operation)['items']


def get_blog_and_api(service: Resource, blog_id: str) -> tuple[Blog, Resource]:
    # Obtengo la API
    post_api = service.posts()

    # Obtengo el blog que está indicado
    my_blogs = get_blogs_of_user()
    try:
        dict_right_blog = next((blog
                                for blog in my_blogs
                                if blog['id'] == blog_id))
    except StopIteration:
        raise ValueError
    right_blog = Blog(**dict_right_blog)

    return right_blog, post_api


@async_initializer
def get_blogger_service():
    return get_google_service(GoogleService.BLOGGER)


# Debido a su decorador, esta función debe declararse después de get_blogger_service
@async_initializer
def get_blogs():
    blogger_service = get_blogger_service()
    return blogger_service.blogs()


# Debido a su decorador, esta función debe declararse después de todas sus dependencias
@async_initializer
def get_posts():
    blogger_service = get_blogger_service()
    blog, posts = get_blog_and_api(blogger_service, BLOG_ID)
    return posts


def insert_post(post: Post, draft: bool) -> None:
    posts = get_posts()
    insert_operation = posts.insert(blogId=BLOG_ID,
                                    body=asdict(post),
                                    isDraft=draft)
    GoogleClient.execute(insert_operation)


def update_post(post: Post) -> None:
    posts = get_posts()
    update_operation = posts.update(blogId=BLOG_ID,
                                    postId=post.id,
                                    body=asdict(post))
    GoogleClient.execute(update_operation)


def delete_post(post: Post) -> None:
    posts = get_posts()
    delete_operation = posts.delete(blogId=BLOG_ID,
                                    postId=post.id)
    GoogleClient.execute(delete_operation)


class PostStatus(str, Enum):
    LIVE = 'LIVE'
    DRAFT = 'DRAFT'
    SCHEDULED = 'SCHEDULED'
    SOFT_TRASHED = 'SOFT_TRASHED'


def list_posts(min_date: str, status: PostStatus, page_token: str) -> tuple[list[dict[str, Any]], str | None]:
    posts = get_posts()
    list_operation = posts.list(blogId=BLOG_ID,
                                status=status.value,
                                startDate=min_date,
                                fields='nextPageToken, items',
                                pageToken=page_token,
                                maxResults=500)

    response: dict = GoogleClient.execute_and_wait(list_operation)

    files_list = response.get('items', [])
    next_page_token = response.get('nextPageToken', None)

    return files_list, next_page_token
