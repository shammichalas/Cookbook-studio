from django.contrib import admin
from .models import Cookbook

@admin.register(Cookbook)
class CookbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'recipe_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'owner__username', 'description')
    prepopulated_fields = {'slug': ('title',)}
