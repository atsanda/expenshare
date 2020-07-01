from django.shortcuts import render
from django.urls import reverse


class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # process only authenticated users and those who wanna login
        if (request.user.is_authenticated or
            request.path.startswith('/social/login') or
            request.path.startswith('/social/complete') or
            request.path.startswith('/social/confirm-registration') or
            request.path.startswith('/terms') or
            request.path.startswith('/policy')
        ):

            response = self.get_response(request)
            return response
        else:
            return render(request, 'main/welcome.html')
