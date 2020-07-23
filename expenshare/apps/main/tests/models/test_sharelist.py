import pytest
from pytest_factoryboy import register
from ...models import Sharelist
from .factories import UserFactory, SharelistFactory


register(UserFactory)
register(SharelistFactory)


@pytest.mark.django_db
def test_are_in_sharelist(user_factory, sharelist_factory):
    user1, user2, user3, user4 = user_factory.create_batch(size=4)
    name = 'some_sharelist'

    sharelist = sharelist_factory.create(name=name, users=[user1, user2, user3])

    assert Sharelist.objects.are_in_sharelist(sharelist.pk, [user1.pk, user2.pk, user3.pk])
    assert not Sharelist.objects.are_in_sharelist(sharelist.pk, [user1.pk, user2.pk, user4.pk])
    assert not Sharelist.objects.are_in_sharelist(sharelist.pk, [-99])
