from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Artwork(models.Model):
    """
    • Originals have parent == None.  
    • Interpretations set parent = original artwork
      (same table, keeps the schema DRY).
    """
    parent = models.ForeignKey(
        "self",
        related_name="interpretations",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="artwork/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Staff set this to ✅ to publish the work (or interpretation).",
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    # Convenience flags -------------------------------------------------------
    @property
    def is_original(self) -> bool:
        return self.parent_id is None

    @property
    def public_interpretations(self):
        return self.interpretations.filter(is_approved=True)


class Comment(models.Model):
    """
    A visitor comment on either an original or an interpretation.
    """
    artwork = models.ForeignKey(
        Artwork, related_name="comments", on_delete=models.CASCADE
    )
    user   = models.ForeignKey(
        User, null=True, blank=True, related_name="comments",
        on_delete=models.SET_NULL,
    )

    name  = models.CharField(max_length=80,  blank=True)   # now blank=True
    email = models.EmailField(blank=True)                  # same here
    text  = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Staff must approve before the comment is visible.",
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.artwork}"
