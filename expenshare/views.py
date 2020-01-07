from django.shortcuts import render
from django.views.generic.edit import CreateView
from expenshare.models import Sharelist
from django.contrib.auth.models import User
from dal import autocomplete
from expenshare.forms import SharelistForm
from django.http import HttpResponse


def index(request):
    context = {
      'sharelists': request.user.sharelist_set.all()
    }
    return render(request, 'expenshare/index.html', context=context)


class SharelistCreate(CreateView):
    model = Sharelist
    template_name = 'expenshare/sharelist_create.html'
    success_url = '/'
    form_class = SharelistForm

    def get_context_data(self, **kwargs):
        ctx = super(SharelistCreate, self).get_context_data(**kwargs)
        ctx['sharelists'] = self.request.user.sharelist_set.all()
        return ctx

    def form_valid(self, form, *args, **kwargs):
        # creator is not selected on the client side, thus shoud bw added by default on server side
        form.cleaned_data['users'] |= User.objects.filter(pk=self.request.user.pk)
        return super().form_valid(form, *args, **kwargs)


class UserAutocomplete(autocomplete.Select2QuerySetView):
    model_field_name = 'username'
    model = User

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(pk=self.request.user.pk)
        return qs
