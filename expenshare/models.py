from urllib.parse import urlsplit
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models import QuerySet, Count
from django.db.models import Prefetch
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
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

    def get_total_credits(self, user_id):
        credit_sum = Coalesce(Sum('credit__amount', filter=Q(credit__creditor=user_id)), 0.0)
        total_credits = self.values('id').annotate(total_credit=credit_sum).values('id', 'total_credit')
        return {c['id']: c['total_credit'] for c in total_credits}

    def get_total_debts(self, user_id):
        debt_sum = Coalesce(Sum('credit__debts__amount', filter=Q(credit__debts__debtor=user_id)), 0.0)
        total_debts = Sharelist.objects.values('id').annotate(total_debt=debt_sum).values('id', 'total_debt')
        return {d['id']: d['total_debt'] for d in total_debts}


class Sharelist(models.Model):
    objects = SharelistQuerySet.as_manager()

    name = models.CharField(max_length=30)
    users = models.ManyToManyField(User)


class CreditQuerySet(QuerySet):
    def get_sharelist_credits_with_user_debt(self, user_id, sharelist_id):
        usr_debts = Debt.objects.filter(debtor_id=user_id)
        qs = self.filter(sharelist_id=sharelist_id).select_related('creditor__profile').prefetch_related(Prefetch('debts', usr_debts))
        return qs

    def is_creator(self, pk, user_id):
        return self.get(id=pk).creditor_id == user_id


class Credit(models.Model):
    objects = CreditQuerySet.as_manager()

    name = models.CharField(max_length=30)
    datetime = models.DateTimeField()
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    creditor = models.ForeignKey(User, on_delete=models.PROTECT)
    sharelist = models.ForeignKey(Sharelist, on_delete=models.PROTECT)


class DebtQuerySet(QuerySet):
    def get_user_debts(self, user_id, sharelist_id, fetch_creditor=True):
        qs = self.filter(debtor=user_id).select_related('credit').filter(credit__sharelist_id=sharelist_id)
        if fetch_creditor:
            qs = qs.select_related('credit__creditor')
            qs = qs.select_related('credit__creditor__profile')
        return qs


class Debt(models.Model):
    objects = DebtQuerySet.as_manager()

    debtor = models.ForeignKey(User, on_delete=models.PROTECT)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='debts')
    amount = models.DecimalField(max_digits=19, decimal_places=2)