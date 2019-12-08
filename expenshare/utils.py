import requests
from requests.status_codes import codes
from django.core.validators import URLValidator
from django.http import Http404


def download_image(url: str, max_size : int = 409_600) -> bytes:
    validate = URLValidator()
    validate(url)

    r = requests.get(url)

    if r.status_code != codes.ok:
        raise Http404('Cannot download image')

    if not r.headers['content-type'].startswith('image'):
        raise ValueError(f'Image expected, got {r.headers["content-type"]}')

    return r.content