from django.shortcuts import render
from django.views.generic.edit import CreateView, FormView
from django.views.generic import TemplateView
from expenshare.models import Sharelist, Record, SharelistUser, Debt
from django.contrib.auth.models import User
from dal import autocomplete
from expenshare.forms import SharelistForm, RecordForm
from django.urls import reverse
from collections import defaultdict


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
        context['active_sharelist_users'] = SharelistUser.objects.filter(sharelist=context['active_sharelist']).select_related('user')

        debts = Debt.objects.filter(sharelist_user__in=context['active_sharelist_users']).select_related('record').order_by('record').all()

        keys = ['name'] + [u.id for u in context['active_sharelist_users']]
        records = defaultdict(lambda: dict.fromkeys(keys))
        for debt in debts:
            records[debt.record_id]['name'] = debt.record.name
            records[debt.record_id][debt.sharelist_user_id] = debt.amount
        context['records'] = dict(records)
        context['columns'] = ['name'] + [u.user.username for u in context['active_sharelist_users']]
        return context


class RecordCreateView(FormView):
    """!TODO check if authorized user is a member of sharelist
    """
    template_name = 'expenshare/record_create.html'
    form_class = RecordForm

    def get_success_url(self):
        return reverse('sharelists-view', kwargs={'sharelist_id': self.kwargs['sharelist_id']})

    def get_form(self):
        sharelist_users = SharelistUser.objects.filter(sharelist=self.kwargs['sharelist_id']).select_related('user').all()
        return RecordForm(sharelist_users, **self.get_form_kwargs())

    def form_valid(self, form):
        data = form.cleaned_data
        record = Record(
            name=data['name'],
            datetime=data['datetime']
            )
        record.save()
        
        # !TODO compute debt here
        pass

        Debt.objects.bulk_create(
            [Debt(sharelist_user=sh_u, record=record, amount=data['amount']) for sh_u in form.sharelist_users]
        )

        return super().form_valid(form)
