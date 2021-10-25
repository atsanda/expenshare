from django.shortcuts import render

from expenshare.sharelists.services import user_sharelists_summary


def index(request):
    if not request.user.is_authenticated:
        return render(request, "index/welcome.html")

    context = {"sharelists": user_sharelists_summary(request.user)}
    return render(request, "index/index.html", context=context)
