from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
)
from django.views.generic.edit import FormMixin

from .forms import ArtworkForm, CommentForm
from .models import Artwork, Comment

from django.views.decorators.clickjacking import xframe_options_exempt


# ---------------------------------------------------------------------------
#  LIST + DETAIL
# ---------------------------------------------------------------------------
# @xframe_options_exempt
class ArtworkListView(ListView):
    """
    Shows only approved originals.
    """
    model = Artwork
    template_name = "gallery/artwork_list.html"
    context_object_name = "artworks"

    def get_queryset(self):
        return (
            Artwork.objects
            .filter(parent__isnull=True, is_approved=True)
        )


class ArtworkDetailView(FormMixin, DetailView):
    """
    Combines:
      • Detail display
      • Comment POST via FormMixin
    """
    model = Artwork
    template_name = "gallery/artwork_detail.html"
    context_object_name = "artwork"
    form_class = CommentForm

    # make `user` available to the form __init__
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            comment = form.save(commit=False)
            comment.artwork = self.object
            comment.is_approved = False    # still moderated

            if request.user.is_authenticated:
                # Auto-fill the model
                comment.user  = request.user
                comment.name = request.user.get_full_name()
                comment.email = request.user.email

            comment.save()
            messages.success(request, "Thanks! Your comment is waiting for staff approval.")
            return redirect(self.get_success_url())

        return self.form_invalid(form)

    # -------------------------------
    # Visibility-/moderation-aware
    # -------------------------------
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_approved and not self.request.user.is_staff:
            raise Http404()
        return obj

    def get_success_url(self):
        return reverse("gallery:artwork_detail", kwargs={"pk": self.object.pk})

    # -------------------------------
    #  Extra context
    # -------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interpretations"]   = self.object.public_interpretations
        context["comment_form"]      = context.get("form")

        # NEW: pre-filtered, approved comments
        context["approved_comments"] = self.object.comments.filter(is_approved=True)
        return context

    # -------------------------------
    #  Accept a new visitor comment
    # -------------------------------
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()          # DetailView requirement
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.artwork = self.object
            comment.is_approved = False          # moderation
            comment.save()
            messages.success(
                request, "Thanks! Your comment is waiting for staff approval."
            )
            return redirect(self.get_success_url())
        return self.form_invalid(form)


# ---------------------------------------------------------------------------
#  CREATE ORIGINAL (staff only)
# ---------------------------------------------------------------------------

class ArtworkCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = Artwork
    form_class = ArtworkForm
    template_name = "gallery/artwork_form.html"
    success_url = reverse_lazy("gallery:artwork_list")

    # staff-only gate
    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        # parent stays None  → original
        form.instance.is_approved = True  # staff originals go live immediately
        return super().form_valid(form)


# ---------------------------------------------------------------------------
#  CREATE INTERPRETATION (any logged-in user)
# ---------------------------------------------------------------------------

class InterpretationCreateView(LoginRequiredMixin, CreateView):
    """
    • Parent artwork is supplied in the URL
    • Interpretation needs approval
    """
    model = Artwork
    form_class = ArtworkForm
    template_name = "gallery/artwork_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.parent = get_object_or_404(
            Artwork,
            pk=self.kwargs["pk"],
            parent__isnull=True,
            is_approved=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.parent = self.parent
        form.instance.uploaded_by = self.request.user
        form.instance.is_approved = False  # staff must approve
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("gallery:artwork_detail", kwargs={"pk": self.parent.pk})
