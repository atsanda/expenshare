from abc import ABC, abstractmethod
from .models import Record, Debt, SharelistUser


class BaseService(ABC):
    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class MakeRecord(BaseService):
    def __init__(self, record_name, record_datetime, amount, sharers, creator_id):
        self._record_name = record_name
        self._record_datetime = record_datetime
        self._amount = amount
        self._sharers = sharers
        self._creator_id = type(sharers[0])(creator_id)

    def execute(self):
        self.validate()

        record = Record(name=self._record_name, datetime=self._record_datetime)
        record.save()

        shrl_usr_to_debt_amnt = self._compute_debts()

        Debt.objects.bulk_create(
            [Debt(sharelist_user_id=sh_u_id, record=record, amount=amnt) for sh_u_id, amnt in shrl_usr_to_debt_amnt.items()]
        )

    def validate(self):
        if not SharelistUser.objects.are_in_the_same_sharelist(self._sharers + [self._creator_id]):
            raise ValueError('Sharers and creator should be in the same sharelist')

    def _compute_debts(self):
        debt = self._amount / len(self._sharers)
        shrl_usr_to_debt_amnt = {u: debt for u in self._sharers}

        if self._creator_id in shrl_usr_to_debt_amnt:
            shrl_usr_to_debt_amnt[self._creator_id] -= self._amount
        else:
            shrl_usr_to_debt_amnt[self._creator_id] = -self._amount

        return shrl_usr_to_debt_amnt
