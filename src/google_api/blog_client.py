from dataclasses import asdict
from enum import Enum
from typing import Any

from googleapiclient.discovery import Resource
from oauth2client import client
from src.config import Config, Param, Section
from src.google_api.api_dataclasses import Blog, Post
from src.google_api.google_api_mgr import get_google_service
from src.google_api.google_client import GoogleClient
from src.thread_safe_property import cach

BLOG_ID = Config.get_value(Section.POST, Param.BLOG_ID)


def get_blog_and_api(service: Resource, blog_id: str) -> tuple[Blog, Resource]:
    try:
        # Obtengo la API
        post_api = service.posts()

        # Obtengo el blog que está indicado
        my_blogs = get_blogs_of_user()
        right_blog = next(
            (blog for blog in my_blogs['items'] if blog['id'] == blog_id), None)
        right_blog = Blog(**right_blog)

        return right_blog, post_api

    except client.AccessTokenRefreshError:
        print('Error en las credenciales')
        return None, None


@cach
def SERVICE():
    return get_google_service('blogger')


@cach
def BLOGS():
    return SERVICE().blogs()


@cach
def POSTS():
    blog, posts = get_blog_and_api(SERVICE(), BLOG_ID)
    return posts


def get_blogs_of_user() -> dict:
    list_operation = BLOGS().listByUser(userId='self')
    return GoogleClient.execute_and_wait(list_operation)


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


class PostStatus(str, Enum):
    LIVE = 'LIVE'
    DRAFT = 'DRAFT'
    SCHEDULED = 'SCHEDULED'
    SOFT_TRASHED = 'SOFT_TRASHED'


def list_posts(min_date: str, status: PostStatus, page_token: str) -> tuple[dict[str, Any], str]:
    list_operation = POSTS().list(blogId=BLOG_ID,
                                  status=status.value,
                                  startDate=min_date,
                                  fields='nextPageToken, items',
                                  pageToken=page_token)

    response: dict = GoogleClient.execute_and_wait(list_operation)

    files_list = response.get('items', [])
    next_page_token = response.get('nextPageToken', None)

    return files_list, next_page_token
