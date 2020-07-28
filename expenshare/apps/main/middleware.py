import re

from django.conf import settings
from django.contrib.auth.decorators import login_required


class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (
            request.user.is_authenticated or
            any(map(lambda regex: re.match(regex, request.path), settings.ALLOW_ANONYMOUS_ACCESS))
        ):
            return None

        return login_required(view_func)(request, *view_args, **view_kwargs)

