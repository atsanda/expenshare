from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SharelistsConfig(AppConfig):
    name = "sharelists"
    verbose_name = _("Sharelists")

    def ready(self):
        try:
            import expenshare.sharelists.signals  # noqa F401
        except ImportError:
            pass
