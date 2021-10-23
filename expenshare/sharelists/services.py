from abc import ABC, abstractmethod

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from expenshare.sharelists.models import Credit, Debt, Sharelist

User = get_user_model()


def user_sharelists_summary(user: User):
    sharelists = user.sharelist_set.all()
    total_credits = Sharelist.objects.get_total_credits(user.id)
    total_debts = Sharelist.objects.get_total_debts(user.id)

    for sh in sharelists:
        sh.total_credit = total_credits[sh.id]
        sh.total_debt = total_debts[sh.id]
        sh.balance = sh.total_credit - sh.total_debt

    return sharelists


class BaseService(ABC):
    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class CreditCreateService(BaseService):
    def __init__(
        self,
        sharelist_id,
        debtor_ids,
        creditor_id,
        credit_name,
        credit_datetime,
        credit_amount,
    ):
        self._sharelist_id = sharelist_id
        self._debtor_ids = debtor_ids
        self._creditor_id = creditor_id
        self._credit_name = credit_name
        self._credit_datetime = credit_datetime
        self._credit_amount = credit_amount

    def execute(self):
        self.validate()

        credit = Credit(
            name=self._credit_name,
            datetime=self._credit_datetime,
            amount=self._credit_amount,
            creditor_id=self._creditor_id,
            sharelist_id=self._sharelist_id,
        )
        credit.save()

        debtors_to_amount = self._compute_debts(self._credit_amount, self._debtor_ids)

        Debt.objects.bulk_create(
            [
                Debt(debtor_id=dbtr_id, credit=credit, amount=amnt)
                for dbtr_id, amnt in debtors_to_amount.items()
            ]
        )

    def validate(self):
        if not Sharelist.objects.are_in_sharelist(
            self._sharelist_id, self._debtor_ids + [self._creditor_id]
        ):
            raise ValueError("Debtors and creditor should be in the same sharelist")

    @staticmethod
    def _compute_debts(credit_amount, debtors):
        debt = credit_amount / len(debtors)
        debtors_to_amount = {u_id: debt for u_id in debtors}
        return debtors_to_amount


class CreditInfoService(BaseService):
    def __init__(self, sharelist_id, credit_id, user_id):
        self._sharelist_id = sharelist_id
        self._credit_id = credit_id
        self._user_id = user_id

    def execute(self):
        self.validate()

        credit = Credit.objects.filter(id=self._credit_id).prefetch_related("debts")[0]
        debts = {d.debtor_id: d for d in credit.debts.all()}

        sharelist_members = User.objects.filter(sharelist=self._sharelist_id).all()
        sharelist_members = {u.id: u for u in sharelist_members}

        debts = [
            {
                "username": sharelist_members[user_id].username,
                "amount": debts[user_id].amount if user_id in debts else 0.0,
            }
            for user_id in sharelist_members
        ]

        info = {
            "name": credit.name,
            "amount": credit.amount,
            "datetime": credit.datetime,
            "debts": debts,
        }

        return info

    def validate(self):
        if not Sharelist.objects.are_in_sharelist(self._sharelist_id, [self._user_id]):
            raise PermissionDenied("User is not authorized to view this credit")


class CreditUpdateService:
    def __init__(
        self,
        credit_id,
        sharelist_id,
        debtor_ids,
        creditor_id,
        credit_name,
        credit_datetime,
        credit_amount,
    ):
        self._credit_id = credit_id
        self._sharelist_id = sharelist_id
        self._debtor_ids = debtor_ids
        self._creditor_id = creditor_id
        self._credit_name = credit_name
        self._credit_datetime = credit_datetime
        self._credit_amount = credit_amount

    def execute(self):
        self.validate()

        credit = (
            Credit.objects.filter(id=self._credit_id).prefetch_related("debts").get()
        )
        debts = credit.debts.all()
        credit_changed = False
        if self._credit_name != credit.name:
            credit.name = self._credit_name
            credit_changed = True
        if self._credit_datetime != credit.datetime:
            credit.datetime = self._credit_datetime
            credit_changed = True
        if self._credit_amount != credit.amount:
            credit.amount = self._credit_amount
            credit_changed = True
        if credit_changed:
            credit.save()

        initial_debtor_ids = [d.debtor_id for d in debts]
        to_delete = [d for d in initial_debtor_ids if d not in self._debtor_ids]
        to_create = [d for d in self._debtor_ids if d not in initial_debtor_ids]

        if to_create or to_delete or self._credit_amount != credit.amount:
            debtors_to_amount = CreditCreateService._compute_debts(
                self._credit_amount, self._debtor_ids
            )

            if to_delete:
                Debt.objects.filter(credit=credit, debtor_id__in=to_delete).delete()

            if to_create:
                Debt.objects.bulk_create(
                    [
                        Debt(debtor_id=dbtr_id, credit=credit, amount=amnt)
                        for dbtr_id, amnt in debtors_to_amount.items()
                        if dbtr_id in to_create
                    ]
                )

            remain_update = [
                d for d in debts if d.debtor_id not in to_create + to_delete
            ]
            for d in remain_update:
                d.amount = debtors_to_amount[d.debtor_id]
            Debt.objects.bulk_update(remain_update, ["amount"])

    def validate(self):
        if not Credit.objects.is_creator(self._credit_id, self._creditor_id):
            raise PermissionDenied("User is not authorized to edit this credit")
        if not Sharelist.objects.are_in_sharelist(
            self._sharelist_id, self._debtor_ids + [self._creditor_id]
        ):
            raise ValueError("Debtors and creditor should be in the same sharelist")


class CreditDeleteService(BaseService):
    def __init__(self, credit_id, user_id):
        self._credit_id = credit_id
        self._user_id = user_id

    def execute(self):
        self.validate()
        Credit.objects.filter(id=self._credit_id).delete()

    def validate(self):
        if not Credit.objects.is_creator(self._credit_id, self._user_id):
            raise PermissionDenied("User is not authorized to delete this credit")
