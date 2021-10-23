# from urllib.parse import urlsplit
from django.db import models
from django.db.models import Prefetch, Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from expenshare.users.models import User


class SharelistQuerySet(QuerySet):
    def are_in_sharelist(self, sharelist_id, user_ids):
        members = self.get(id=sharelist_id).users.values("id").all()
        members = [m["id"] for m in members]
        # in case of duplications
        user_ids = set(user_ids)

        if len(user_ids) > len(members):
            return False

        res = True
        for u in user_ids:
            res &= u in members

        return res

    def get_total_credits(self, user_id):
        credit_sum = Coalesce(
            Sum("credit__amount", filter=Q(credit__creditor=user_id)), 0.0
        )
        total_credits = (
            self.values("id")
            .annotate(total_credit=credit_sum)
            .values("id", "total_credit")
        )
        return {c["id"]: c["total_credit"] for c in total_credits}

    def get_total_debts(self, user_id):
        debt_sum = Coalesce(
            Sum("credit__debts__amount", filter=Q(credit__debts__debtor=user_id)), 0.0
        )
        total_debts = (
            Sharelist.objects.values("id")
            .annotate(total_debt=debt_sum)
            .values("id", "total_debt")
        )
        return {d["id"]: d["total_debt"] for d in total_debts}

    def get_user_debts_per_member(self, sharelist_id, user_id):
        debts = (
            Debt.objects.filter(credit__sharelist__id=sharelist_id, debtor=user_id)
            .values("credit__creditor")
            .annotate(debt_amount=Sum("amount"))
            .values("credit__creditor", "debt_amount")
        )
        member_to_user_debt = {d["credit__creditor"]: d["debt_amount"] for d in debts}
        return member_to_user_debt

    def get_user_credits_per_member(self, sharelist_id, user_id):
        credits = (
            Credit.objects.filter(sharelist__id=sharelist_id, creditor=user_id)
            .values("debts__debtor")
            .annotate(credit_amount=Sum("debts__amount"))
            .values("debts__debtor", "credit_amount")
        )
        member_to_user_credit = {
            c["debts__debtor"]: c["credit_amount"] for c in credits
        }
        return member_to_user_credit


class Sharelist(models.Model):
    objects = SharelistQuerySet.as_manager()

    name = models.CharField(max_length=30)
    users = models.ManyToManyField(User)


class CreditQuerySet(QuerySet):
    def get_sharelist_credits_with_user_debt(self, user_id, sharelist_id):
        usr_debts = Debt.objects.filter(debtor_id=user_id)
        qs = (
            self.filter(sharelist_id=sharelist_id)
            .select_related("creditor__profile")
            .prefetch_related(Prefetch("debts", usr_debts))
        )
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
        qs = (
            self.filter(debtor=user_id)
            .select_related("credit")
            .filter(credit__sharelist_id=sharelist_id)
        )
        if fetch_creditor:
            qs = qs.select_related("credit__creditor")
            qs = qs.select_related("credit__creditor__profile")
        return qs


class Debt(models.Model):
    objects = DebtQuerySet.as_manager()

    debtor = models.ForeignKey(User, on_delete=models.PROTECT)
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name="debts")
    amount = models.DecimalField(max_digits=19, decimal_places=2)
