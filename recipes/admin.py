from django.contrib import admin
from .models import Category, Tag, Recipe, RecipeIngredient, RecipeStep, RecipeComment, RecipeLike, NewsletterSubscriber

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'difficulty', 'is_draft', 'view_count', 'like_count', 'created_at')
    list_filter = ('is_draft', 'category', 'difficulty', 'created_at')
    search_fields = ('title', 'author__username', 'description', 'chef_notes')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [RecipeIngredientInline, RecipeStepInline]
    actions = ['publish_recipes', 'draft_recipes']

    def publish_recipes(self, request, queryset):
        queryset.update(is_draft=False)
        self.message_user(request, "Selected recipes have been published.")
    publish_recipes.short_description = "Publish selected recipes"

    def draft_recipes(self, request, queryset):
        queryset.update(is_draft=True)
        self.message_user(request, "Selected recipes have been set to drafts.")
    draft_recipes.short_description = "Revert selected recipes to draft"

    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count')
    prepopulated_fields = {'slug': ('name',)}

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Number of Recipes'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'recipe__title')

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    ordering = ('-subscribed_at',)

admin.site.register(RecipeLike)
