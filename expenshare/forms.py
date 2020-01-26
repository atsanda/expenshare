from dal import autocomplete
from django import forms
from expenshare.models import Sharelist
from django.contrib.auth.models import User
from django.utils import timezone


class SharelistForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete', attrs={'data-placeholder': 'Autocomplete ...'})
    )

    class Meta:
        model = Sharelist
        fields = ('__all__')


class CreditForm(forms.Form):
    name = forms.CharField(label='Name', max_length=30)
    datetime = forms.DateTimeField(label='Datetime', initial=timezone.now())
    amount = forms.DecimalField(max_digits=19, decimal_places=4)

    def __init__(self, debtors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debtors = debtors
        choices = [(d.id, d.username) for d in debtors]

        self.fields['debtors'] = forms.MultipleChoiceField(
            choices=choices,
            widget=forms.CheckboxSelectMultiple,
            initial=[c[0] for c in choices]
        )

    def is_valid(self):
        res = super().is_valid()
        self.cleaned_data['debtors'] = [int(d) for d in self.cleaned_data['debtors']]
        return res