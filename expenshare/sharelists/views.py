# from social_django.utils import load_strategy
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.views.generic.edit import CreateView, FormView

from .forms import CreditForm, SharelistForm
from .models import Credit, Sharelist
from .services import (
    CreditCreateService,
    CreditDeleteService,
    CreditInfoService,
    CreditUpdateService,
)

User = get_user_model()


class SharelistCreate(LoginRequiredMixin, CreateView):
    model = Sharelist
    template_name = "sharelists/sharelist_create.html"
    success_url = "/"
    form_class = SharelistForm

    def form_valid(self, form, *args, **kwargs):
        # creator is not selected on the client side, thus shoud bw added by default on server side
        form.cleaned_data["users"] |= User.objects.filter(pk=self.request.user.pk)
        return super().form_valid(form, *args, **kwargs)


class SharelistMain(LoginRequiredMixin, TemplateView):
    template_name = "sharelists/sharelist_view_main.html"
    nbar = "main"
    pagination_limit = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_sharelist"] = Sharelist.objects.get(id=context["sharelist_id"])

        paginator = Paginator(
            Credit.objects.get_sharelist_credits_with_user_debt(
                self.request.user.pk, context["sharelist_id"]
            ),
            self.pagination_limit,
        )

        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        context["paginator"] = paginator
        context["page_obj"] = page_obj
        context["nbar"] = self.nbar
        return context


class SharelistSummary(LoginRequiredMixin, TemplateView):
    template_name = "sharelists/sharelist_view_summary.html"
    nbar = "summary"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_sharelist"] = Sharelist.objects.get(id=context["sharelist_id"])

        member_to_user_debt = Sharelist.objects.get_user_debts_per_member(
            context["sharelist_id"], self.request.user.id
        )
        member_to_user_credit = Sharelist.objects.get_user_credits_per_member(
            context["sharelist_id"], self.request.user.id
        )

        per_member_summary = [
            {
                "id": u.id,
                "username": u.username,
                "user_debt": member_to_user_debt.get(u.id, Decimal(0.0)),
                "user_credit": member_to_user_credit.get(u.id, Decimal(0.0)),
            }
            for u in context["active_sharelist"].users.all()
            if u.id != self.request.user.id
        ]

        for entity in per_member_summary:
            entity["user_balance"] = entity["user_credit"] - entity["user_debt"]

        context["per_member_summary"] = per_member_summary
        context["nbar"] = self.nbar
        return context


class CreditFormView(LoginRequiredMixin, FormView):
    form_class = CreditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"sharelist_id": self.kwargs["sharelist_id"]})
        return kwargs


class CreditCreate(CreditFormView):
    template_name = "sharelists/credit_create.html"

    def get_success_url(self):
        return reverse(
            "sharelists:view", kwargs={"sharelist_id": self.kwargs["sharelist_id"]}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["button_name"] = "Create"
        return kwargs

    def form_valid(self, form):
        service = CreditCreateService(
            self.kwargs["sharelist_id"],
            form.cleaned_data["debtors"],
            self.request.user.pk,
            form.cleaned_data["name"],
            form.cleaned_data["datetime"],
            form.cleaned_data["amount"],
        )
        service.execute()
        return super().form_valid(form)


class CreditUpdate(CreditFormView):
    template_name = "sharelists/credit_create.html"

    def get_success_url(self):
        return reverse(
            "sharelists:credits-view",
            kwargs={
                "sharelist_id": self.kwargs["sharelist_id"],
                "credit_id": self.kwargs["credit_id"],
            },
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        credit_obj = (
            Credit.objects.filter(id=self.kwargs["credit_id"])
            .prefetch_related("debts")
            .get()
        )
        data = {
            "name": credit_obj.name,
            "datetime": credit_obj.datetime,
            "amount": credit_obj.amount,
            "debtors": [d.debtor_id for d in credit_obj.debts.all()],
        }

        kwargs["initial"] = data
        kwargs["button_name"] = "Update"
        return kwargs

    def form_valid(self, form):
        service = CreditUpdateService(
            self.kwargs["credit_id"],
            self.kwargs["sharelist_id"],
            form.cleaned_data["debtors"],
            self.request.user.pk,
            form.cleaned_data["name"],
            form.cleaned_data["datetime"],
            form.cleaned_data["amount"],
        )
        service.execute()
        return super().form_valid(form)


class CreditView(LoginRequiredMixin, TemplateView):
    template_name = "sharelists/credit_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        service = CreditInfoService(
            context["sharelist_id"], context["credit_id"], self.request.user.pk
        )
        credit_info = service.execute()
        context["credit_info"] = credit_info
        return context


class CreditDelete(LoginRequiredMixin, View):
    pattern_name = "sharelists:view"

    def delete(self, request, *args, **kwargs):
        credit_id = kwargs.pop("credit_id", None)

        service = CreditDeleteService(
            credit_id,
            self.request.user.pk,
        )

        try:
            service.execute()
        except PermissionDenied as e:
            return HttpResponseForbidden(content=str(e))

        url = reverse(self.pattern_name, kwargs=kwargs)
        return JsonResponse(data={"success_url": url}, status=200)
