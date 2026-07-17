from django.db import models
from django.conf import settings
from django.utils.text import slugify
from recipes.models import Recipe

class Cookbook(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cookbooks')
    cover_image = models.ImageField(upload_to='cookbooks/covers/', default='cookbooks/covers/default.jpg', blank=True)
    description = models.TextField(blank=True, help_text="A brief introduction to your collection.")
    recipes = models.ManyToManyField(Recipe, related_name='cookbooks', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Cookbook.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def recipe_count(self):
        return self.recipes.count()
