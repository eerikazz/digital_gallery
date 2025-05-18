from django import forms
from .models import Artwork, Comment


class ArtworkForm(forms.ModelForm):
    """
    Used for BOTH originals and interpretations.
    Staff-only view will make parent=None;
    interpretation view will set parent in the view’s form_valid().
    """
    class Meta:
        model = Artwork
        fields = ["title", "description", "image"]


class CommentForm(forms.ModelForm):
    class Meta:
        model  = Comment
        fields = ["name", "email", "text"]

    # 👇 inject the request.user object when the form is built
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            # logged-in users don’t need to type name/email
            self.fields.pop("name")
            self.fields.pop("email")

