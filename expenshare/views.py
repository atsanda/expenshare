from django.shortcuts import render
from django.views.generic.edit import CreateView, FormView
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse
from expenshare.models import Sharelist, Credit
from django.contrib.auth.models import User
from dal import autocomplete
from expenshare.forms import SharelistForm, CreditForm
from .services import CreditCreateService, CreditInfoService, \
    CreditUpdateService, CreditDeleteService
from django.http import HttpResponseForbidden, JsonResponse
from django.core.exceptions import PermissionDenied


def index(request):
    sharelists = Sharelist.objects.order_by('id').all()
    total_credits = Sharelist.objects.get_total_credits(request.user.id)
    total_debts = Sharelist.objects.get_total_debts(request.user.id)

    for sh in sharelists:
        sh.total_credit = total_credits[sh.id]
        sh.total_debt = total_debts[sh.id]
        sh.balance = sh.total_credit - sh.total_debt

    context = {
      'sharelists': sharelists
    }
    return render(request, 'expenshare/index.html', context=context)


class SharelistCreate(CreateView):
    model = Sharelist
    template_name = 'expenshare/sharelist_create.html'
    success_url = '/'
    form_class = SharelistForm

    def form_valid(self, form, *args, **kwargs):
        # creator is not selected on the client side, thus shoud bw added by default on server side
        form.cleaned_data['users'] |= User.objects.filter(pk=self.request.user.pk)
        return super().form_valid(form, *args, **kwargs)


class UserAutocomplete(autocomplete.Select2QuerySetView):
    model_field_name = 'username'
    model = User

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(pk=self.request.user.pk)[:5]
        return qs


class SharelistView(TemplateView):
    template_name = 'expenshare/sharelist_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_sharelist'] = Sharelist.objects.get(id=context['sharelist_id'])

        paginator = Paginator(
            Credit.objects.get_sharelist_credits_with_user_debt(self.request.user.pk, context['sharelist_id']),
            settings.DEBTS_PER_PAGE,
            )

        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page_obj
        return context


class CreditFormView(FormView):
    form_class = CreditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'sharelist_id': self.kwargs['sharelist_id']
        })
        return kwargs


class CreditCreate(CreditFormView):
    template_name = 'expenshare/credit_create.html'

    def get_success_url(self):
        return reverse('sharelists-view', kwargs={'sharelist_id': self.kwargs['sharelist_id']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['button_name'] = 'Create'
        return kwargs

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


class CreditUpdate(CreditFormView):
    template_name = 'expenshare/credit_create.html'

    def get_success_url(self):
        return reverse(
            'credits-view',
            kwargs={
                'sharelist_id': self.kwargs['sharelist_id'], 
                'credit_id': self.kwargs['credit_id']}
            )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        credit_obj = Credit.objects.filter(id=self.kwargs['credit_id']).prefetch_related('debts').get()
        data = {
            'name': credit_obj.name,
            'datetime': credit_obj.datetime,
            'amount': credit_obj.amount,
            'debtors': [d.debtor_id for d in credit_obj.debts.all()]
        }
        
        kwargs['initial'] = data
        kwargs['button_name'] = 'Update'
        return kwargs

    def form_valid(self, form):
        service = CreditUpdateService(
            self.kwargs['credit_id'],
            self.kwargs['sharelist_id'],
            form.cleaned_data['debtors'],
            self.request.user.pk,
            form.cleaned_data['name'],
            form.cleaned_data['datetime'],
            form.cleaned_data['amount'],
            )
        service.execute()
        return super().form_valid(form)


class CreditView(TemplateView):
    template_name = 'expenshare/credit_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        service = CreditInfoService(context['sharelist_id'], context['credit_id'], self.request.user.pk)
        credit_info = service.execute()
        context['credit_info'] = credit_info
        return context


class CreditDelete(View):
    pattern_name = 'sharelists-view'

    def delete(self, request, *args, **kwargs):
        credit_id = kwargs.pop('credit_id', None)

        service = CreditDeleteService(
            credit_id,
            self.request.user.pk,
            )

        try:
            service.execute()
        except PermissionDenied as e:
            return HttpResponseForbidden(content=str(e))

        url = reverse(self.pattern_name, kwargs=kwargs)
        return JsonResponse(data={'success_url': url}, status=200)