from dal import autocomplete
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Hidden
from expenshare.models import Sharelist
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class SharelistForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects,
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete', attrs={'data-placeholder': 'Autocomplete ...'})
    )

    class Meta:
        model = Sharelist
        fields = ('__all__')


class CreditForm(forms.Form):
    name = forms.CharField(label='Name', max_length=30)
    datetime = forms.DateTimeField(label='Datetime', initial=timezone.now())
    amount = forms.DecimalField(max_digits=19, decimal_places=4)

    def __init__(self, sharelist_id, button_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debtors = Sharelist.objects.get(id=sharelist_id).users.all()
        choices = [(d.id, d.username) for d in self.debtors]

        self.fields['debtors'] = forms.MultipleChoiceField(
            choices=choices,
            widget=forms.CheckboxSelectMultiple,
            initial=[c[0] for c in choices]
        )

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', button_name))

    def is_valid(self):
        res = super().is_valid()
        self.cleaned_data['debtors'] = [int(d) for d in self.cleaned_data['debtors']]
        return res


class RegistrationConfirmationFrom(forms.Form):
    partial_token = forms.CharField(widget=forms.HiddenInput())
    username = forms.CharField(label='Username', disabled=True)
    email = forms.CharField(label='Email', disabled=True)
    rules_accepted = forms.BooleanField()
    acceptance_label_template = 'I accept <a href="%(terms_url)s">terms of use</a> and <a href="%(policy_url)s">personal data processing policy</a>'

    def __init__(self, partial_backend_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        urls = {'terms_url': reverse('terms'), 'policy_url': reverse('policy')}
        self.fields['rules_accepted'].label = self.acceptance_label_template % urls
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.form_action = reverse("social:complete", kwargs={'backend': partial_backend_name})