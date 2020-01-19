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


class RecordForm(forms.Form):
    name = forms.CharField(label='Name', max_length=30)
    datetime = forms.DateTimeField(label='Datetime', initial=timezone.now())
    amount = forms.DecimalField(max_digits=19, decimal_places=4)

    def __init__(self, sharelist_users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sharelist_users = sharelist_users
        choices = [(u.id, u.user.username) for u in sharelist_users]

        self.fields['debitors'] = forms.MultipleChoiceField(
            choices=choices,
            widget=forms.CheckboxSelectMultiple,
            initial=[c[0] for c in choices]
        )

    def is_valid(self):
        res = super().is_valid()
        filtered_users = [u for u in self.sharelist_users if str(u.id) in self.cleaned_data['debitors']]
        res &= len(filtered_users) == len(self.cleaned_data['debitors'])
        res &= all([filtered_users[0].sharelist_id == fu.sharelist_id for fu in filtered_users])
        return res
