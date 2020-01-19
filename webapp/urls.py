"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from django.contrib.auth.views import LogoutView
import expenshare.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', expenshare.views.index, name='index'),
    path('logout', LogoutView.as_view(next_page='/'), name='logout'),
    path('social/', include('social_django.urls', namespace='social')),
    path('sharelists/create', expenshare.views.SharelistCreate.as_view(), name="sharelists-create"),
    path('sharelists/<int:sharelist_id>', expenshare.views.SharelistView.as_view(), name='sharelists-view'),
    path('sharelists/<int:sharelist_id>/records/create', expenshare.views.RecordCreateView.as_view(), name='records-create'),
    path('user-autocomplete/', expenshare.views.UserAutocomplete.as_view(), name='user-autocomplete'),
]
