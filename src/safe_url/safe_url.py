from http import HTTPStatus

from requests.models import Response

from .http_utils import safe_response
from .pass_captcha import PassCaptcha


def safe_get_url(url: str) -> Response:
    # open with GET method
    resp = safe_response(url)
    # Caso 429: too many requests
    if resp.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        return PassCaptcha(url)
    else:
        return resp
