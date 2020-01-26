from django.shortcuts import render
from django.views.generic.edit import CreateView, FormView
from django.views.generic import TemplateView
from expenshare.models import Sharelist, Credit, Debt
from django.contrib.auth.models import User
from dal import autocomplete
from expenshare.forms import SharelistForm, CreditForm
from django.urls import reverse
from collections import defaultdict
from .services import CreditCreateService, CreditsTableGetService


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


class SharelistView(TemplateView):
    template_name = 'expenshare/sharelist_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sharelists'] = self.request.user.sharelist_set.all()
        context['active_sharelist'] = next(filter(lambda sl: sl.id == context['sharelist_id'], context['sharelists']), None)
        
        service = CreditsTableGetService(context['active_sharelist'].id)
        context['credits_table'] = service.execute()
        return context


class CreditCreateView(FormView):
    template_name = 'expenshare/credit_create.html'
    form_class = CreditForm

    def get_success_url(self):
        return reverse('sharelists-view', kwargs={'sharelist_id': self.kwargs['sharelist_id']})

    def get_form(self):
        debtors = Sharelist.objects.get(id=self.kwargs['sharelist_id']).users.all()
        return CreditForm(debtors, **self.get_form_kwargs())

    def form_valid(self, form):
        service = CreditCreateService(
            self.kwargs['sharelist_id'],
            form.cleaned_data['debtors'],
            self.request.user.pk,
            form.cleaned_data['name'],
            form.cleaned_data['datetime'],
            form.cleaned_data['amount']
            )
        service.execute()
        return super().form_valid(form)
