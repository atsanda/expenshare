import factory
from factory.django import DjangoModelFactory

from ...models import Sharelist


class SharelistFactory(DjangoModelFactory):
    class Meta:
        model = Sharelist

    name = factory.Sequence(lambda n: f"sharelist{n}")

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.users.add(*extracted)
