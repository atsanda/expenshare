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


class SharelistQuerySet(QuerySet):
    def are_in_sharelist(self, sharelist_id, user_ids):
        members = self.get(id=sharelist_id).users.values('id').all()
        members = [m['id'] for m in members]
        # in case of duplications
        user_ids = set(user_ids)

        if len(user_ids) > len(members):
            return False

        res = True
        for u in user_ids:
            res &= (u in members)

        return res


class Sharelist(models.Model):
    objects = SharelistQuerySet.as_manager()

    name = models.CharField(max_length=30)
    users = models.ManyToManyField(User)


class Credit(models.Model):
    name = models.CharField(max_length=30)
    datetime = models.DateTimeField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    creditor = models.ForeignKey(User, on_delete=models.PROTECT)
    sharelist = models.ForeignKey(Sharelist, on_delete=models.PROTECT)


class Debt(models.Model):
    debtor = models.ForeignKey(User, on_delete=models.PROTECT)
    credit = models.ForeignKey(Credit, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=19, decimal_places=4)