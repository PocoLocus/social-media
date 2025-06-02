from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import Post, Comment, Tag, CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "image", "get_groups", "is_staff", "is_superuser", "is_active", "last_login", "date_joined"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["author", "created_at", "updated_at", "get_tags"]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Tag)

