from django.contrib import admin

from expenshare.sharelists.models import Credit, Debt, Sharelist

for model in (Sharelist, Credit, Debt):
    admin.site.register(model)
