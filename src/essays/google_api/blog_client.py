from dataclasses import asdict
from enum import Enum
from functools import cache
from typing import Any

from googleapiclient.discovery import Resource

from src.config import Config, Param, Section

from .api_dataclasses import Blog, Post
from .google_api_mgr import get_google_service, GoogleService
from .google_client import GoogleClient

BLOG_ID = Config.get_value(Section.POST, Param.BLOG_ID)


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


@cache
def SERVICE():
    return get_google_service(GoogleService.BLOGGER)


@cache
def BLOGS():
    return SERVICE().blogs()


@cache
def POSTS():
    blog, posts = get_blog_and_api(SERVICE(), BLOG_ID)
    return posts


def get_blogs_of_user() -> list[dict[str, Any]]:
    list_operation = BLOGS().listByUser(userId='self')
    return GoogleClient.execute_and_wait(list_operation)['items']


def insert_post(post: Post, draft: bool) -> None:
    insert_operation = POSTS().insert(blogId=BLOG_ID,
                                      body=asdict(post),
                                      isDraft=draft)
    GoogleClient.execute(insert_operation)


def update_post(post: Post) -> None:
    update_operation = POSTS().update(blogId=BLOG_ID,
                                      postId=post.id,
                                      body=asdict(post))
    GoogleClient.execute(update_operation)


def delete_post(post: Post) -> None:
    delete_operation = POSTS().delete(blogId=BLOG_ID,
                                      postId=post.id)
    GoogleClient.execute(delete_operation)


class PostStatus(str, Enum):
    LIVE = 'LIVE'
    DRAFT = 'DRAFT'
    SCHEDULED = 'SCHEDULED'
    SOFT_TRASHED = 'SOFT_TRASHED'


def list_posts(min_date: str, status: PostStatus, page_token: str) -> tuple[list[dict[str, Any]], str | None]:
    list_operation = POSTS().list(blogId=BLOG_ID,
                                  status=status.value,
                                  startDate=min_date,
                                  fields='nextPageToken, items',
                                  pageToken=page_token,
                                  maxResults=500)

    response: dict = GoogleClient.execute_and_wait(list_operation)

    files_list = response.get('items', [])
    next_page_token = response.get('nextPageToken', None)

    return files_list, next_page_token
