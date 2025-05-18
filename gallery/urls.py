from django.urls import path
from .views import (
    ArtworkListView,
    ArtworkDetailView,
    ArtworkCreateView,
    InterpretationCreateView,
)

app_name = "gallery"

urlpatterns = [
    # ---------- public ----------
    path("", ArtworkListView.as_view(), name="artwork_list"),
    path("artwork/<int:pk>/", ArtworkDetailView.as_view(), name="artwork_detail"),

    # ---------- create ----------
    path("artwork/add/", ArtworkCreateView.as_view(), name="artwork_add"),  # staff
    path(
        "artwork/<int:pk>/interpretation/add/",
        InterpretationCreateView.as_view(),
        name="interpretation_add",
    ),
]
