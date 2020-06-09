from social_core.pipeline.partial import partial
from django.urls import reverse


@partial
def confirm_registration(strategy, details, user=None, is_new=False, *args, **kwargs):
    rules_accepted = strategy.request_data().get('rules_accepted')
    if is_new and rules_accepted != 'on':
        current_partial = kwargs.get('current_partial')
        return strategy.redirect(
            reverse('confirm-registration') + '?partial_token={0}'.format(current_partial.token)
        )