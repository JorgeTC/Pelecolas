from http import HTTPStatus
import logging

from requests.models import Response

from .http_utils import safe_response
from .pass_captcha import PassCaptcha


def safe_get_url(url: str) -> Response:
    logging.debug(f"Requesting url: {url}")
    # open with GET method
    resp = safe_response(url)
    # Caso 429: too many requests
    if resp.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        logging.debug(f"Too many requests for url: {url}")
        return PassCaptcha(url)
    else:
        return resp
