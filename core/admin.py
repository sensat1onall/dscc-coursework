from django.contrib import admin
from .models import Category, Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "created_at")
    list_filter = ("created_at", "status", "category")
    search_fields = ("title", "description")
    autocomplete_fields = ("category", "collaborators")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "task", "created_at")
    list_filter = ("created_at",)
