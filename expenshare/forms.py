from dal import autocomplete
from django import forms
from expenshare.models import Sharelist
from django.contrib.auth.models import User


class SharelistForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='user-autocomplete', attrs={'data-placeholder': 'Autocomplete ...'})
    )

    class Meta:
        model = Sharelist
        fields = ('__all__')
