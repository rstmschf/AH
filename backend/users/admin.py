from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ("id", "username", "email", "is_hidden", "is_staff", "is_active")
    list_filter = (
        "is_active",
        "is_hidden",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("Moderation", {"fields": ("is_hidden", "is_deleted", "deleted_at")}),
    )

    def delete_model(self, request, obj):
        obj.soft_delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.soft_delete()
