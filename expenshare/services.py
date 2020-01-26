from abc import ABC, abstractmethod
from collections import defaultdict
from .models import Credit, Debt, Sharelist


class BaseService(ABC):
    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class CreditCreateService(BaseService):
    def __init__(self, sharelist_id, debtor_ids, creditor_id, credit_name, credit_datetime, credit_amount):
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
            sharelist_id=self._sharelist_id)
        credit.save()

        debtors_to_amount = self._compute_debts()

        Debt.objects.bulk_create(
            [Debt(debtor_id=dbtr_id, credit=credit, amount=amnt) for dbtr_id, amnt in debtors_to_amount.items()]
        )

    def validate(self):
        if not Sharelist.objects.are_in_sharelist(self._sharelist_id, self._debtor_ids + [self._creditor_id]):
            raise ValueError('Debtors and creditor should be in the same sharelist')

    def _compute_debts(self):
        debt = self._credit_amount / len(self._debtor_ids)
        debtors_to_amount = {u_id: debt for u_id in self._debtor_ids}
        return debtors_to_amount


class CreditsTableGetService(BaseService):

    def __init__(self, sharelist_id):
        self.sharelist_id = sharelist_id

    def validate(self):
        pass

    def _get_row_dict_template(self, keys, defaults):
        row_dict = dict.fromkeys(keys)
        for k, default_value in defaults.items():
            row_dict[k] = default_value
        return row_dict

    def execute(self):
        self.validate()

        members = Sharelist.objects.get(id=self.sharelist_id).users.all()
        members_to_username = {m.id: m.username for m in members}
        credits = Credit.objects.filter(sharelist_id=self.sharelist_id)
        debts = Debt.objects.filter(credit__in=credits).select_related('credit')

        columns = ['creditor', 'name'] + [username for _, username in members_to_username.items()]
        keys = ['creditor', 'name'] + [id for id, _ in members_to_username.items()]
        defaults = {id: 0 for id, _ in members_to_username.items()}
        rows = defaultdict(lambda: self._get_row_dict_template(keys, defaults))
        for debt in debts:
            rows[debt.credit_id]['creditor'] = members_to_username[debt.credit.creditor_id]
            rows[debt.credit_id]['name'] = debt.credit.name
            rows[debt.credit_id][debt.debtor_id] = debt.amount

        rows = [[value for _, value in values_dict.items()] for _, values_dict in rows.items()]
        return {'columns': columns, 'rows': rows}
