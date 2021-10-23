import factory
from django.contrib.auth.models import Group, User

from ...models import Sharelist


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"john{n}")
    email = factory.Sequence(lambda n: f"lennon{n}@thebeatles.com")
    password = factory.PostGenerationMethodCall("set_password", "johnpassword")

    @factory.post_generation
    def has_default_group(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            default_group, _ = Group.objects.get_or_create(name="group")
            self.groups.add(default_group)


class SharelistFactory(factory.DjangoModelFactory):
    class Meta:
        model = Sharelist

    name = factory.Sequence(lambda n: f"sharelist{n}")

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.users.add(*extracted)
