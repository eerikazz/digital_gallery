from django.contrib import admin
from .models import Artwork, Comment


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "parent", "is_approved", "uploaded_at")
    list_filter = ("is_approved",)
    search_fields = ("title",)
    actions = ["approve_selected"]

    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} artwork(s) approved.")
    approve_selected.short_description = "Approve selected artwork"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("artwork", "name", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("name", "text")
    actions = ["approve_selected"]

    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} comment(s) approved.")
    approve_selected.short_description = "Approve selected comments"
