from django.urls import path

from expenshare.sharelists.views import (
    CreditCreate,
    CreditDelete,
    CreditUpdate,
    CreditView,
    SharelistCreate,
    SharelistMain,
    SharelistSummary,
)

app_name = "sharelists"
urlpatterns = [
    path("create", SharelistCreate.as_view(), name="create"),
    path("<int:sharelist_id>", SharelistMain.as_view(), name="view"),
    path("<int:sharelist_id>/summary", SharelistSummary.as_view(), name="summary"),
    path(
        "<int:sharelist_id>/credits/create",
        CreditCreate.as_view(),
        name="credits-create",
    ),
    path(
        "<int:sharelist_id>/credits/<int:credit_id>",
        CreditView.as_view(),
        name="credits-view",
    ),
    path(
        "<int:sharelist_id>/credits/<int:credit_id>/update",
        CreditUpdate.as_view(),
        name="credits-update",
    ),
    path(
        "<int:sharelist_id>/credits/<int:credit_id>/delete",
        CreditDelete.as_view(),
        name="credits-delete",
    ),
]
