from urllib.parse import urlsplit
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from .utils import download_image


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile/photos/%Y/%m/%d')

 
def save_profile_oauth_pipline(backend, user, response, *args, **kwargs):
    if kwargs['is_new'] == True:
        photo_url = None
        if backend.name == 'vk-oauth2':
            photo_url = response['photo']
        
        photo = download_image(photo_url)
        ext = urlsplit(photo_url).path
        ext = ext[ext.rfind('.'):]
        profile = Profile(user=user)
        profile.photo.save(f'{user.username}.{ext}', ContentFile(photo))
        profile.save()


