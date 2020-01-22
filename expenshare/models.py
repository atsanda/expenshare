from urllib.parse import urlsplit
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import QuerySet, Count
from .utils import download_image


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile/photos/%Y/%m/%d')


def save_profile_oauth_pipline(backend, user, response, *args, **kwargs):
    if kwargs['is_new']:
        photo_url = None
        if backend.name == 'vk-oauth2':
            photo_url = response['photo']

        photo = download_image(photo_url)
        ext = urlsplit(photo_url).path
        ext = ext[ext.rfind('.'):]
        profile = Profile(user=user)
        profile.photo.save(f'{user.username}.{ext}', ContentFile(photo))
        profile.save()


class Sharelist(models.Model):
    name = models.CharField(max_length=30)
    users = models.ManyToManyField(User, through='SharelistUser')


class SharelistUserQuerySet(QuerySet):
    def are_in_the_same_sharelist(self, sharelist_user_ids):
        res = self.filter(id__in=sharelist_user_ids).aggregate(Count('sharelist', distinct=True))
        return res['sharelist__count'] == 1


class SharelistUser(models.Model):
    objects = SharelistUserQuerySet.as_manager()

    sharelist = models.ForeignKey(Sharelist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)


class Record(models.Model):
    name = models.CharField(max_length=30)
    datetime = models.DateTimeField()


class Debt(models.Model):
    sharelist_user = models.ForeignKey(SharelistUser, on_delete=models.PROTECT)
    record = models.ForeignKey(Record, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=19, decimal_places=4)