"""expenshare URL Configuration

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
from expenshare.apps.main.views import (
    index, ConfirmRegistration, SharelistCreate, SharelistMain, SharelistSummary, CreditCreate, 
    CreditView, CreditUpdate, CreditDelete, Policy, Terms, UserAutocomplete
    )
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('logout', LogoutView.as_view(next_page='/'), name='logout'),
    path('social/', include('social_django.urls', namespace='social')),
    path('social/confirm-registration', ConfirmRegistration.as_view(), name="confirm-registration"),
    path('sharelists/create', SharelistCreate.as_view(), name="sharelists-create"),
    path('sharelists/<int:sharelist_id>', SharelistMain.as_view(), name='sharelists-view'),
    path('sharelists/<int:sharelist_id>/summary', SharelistSummary.as_view(), name='sharelists-summary'),
    path('sharelists/<int:sharelist_id>/credits/create', CreditCreate.as_view(), name='credits-create'),
    path('sharelists/<int:sharelist_id>/credits/<int:credit_id>', CreditView.as_view(), name='credits-view'),
    path('sharelists/<int:sharelist_id>/credits/<int:credit_id>/update', CreditUpdate.as_view(), name='credits-update'),
    path('sharelists/<int:sharelist_id>/credits/<int:credit_id>/delete', CreditDelete.as_view(), name='credits-delete'),
    path('policy', Policy.as_view(), name='policy'),
    path('terms', Terms.as_view(), name='terms'),
    path('user-autocomplete/', UserAutocomplete.as_view(), name='user-autocomplete'),
]