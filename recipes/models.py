from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon_image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    cover_image = models.ImageField(upload_to='recipes/covers/', default='recipes/covers/default.jpg', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='recipes')
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipes')
    
    # Recipe metadata
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=10)
    cook_time = models.PositiveIntegerField(help_text="Cooking time in minutes", default=20)
    servings = models.PositiveIntegerField(default=4)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Medium')
    
    # Detailed fields
    description = CKEditor5Field('Description', config_name='extends', blank=True)
    chef_notes = models.TextField(blank=True, help_text="Extra tips, tricks, and flavor notes from the chef.")
    
    # Nutrition fields
    nutrition_calories = models.PositiveIntegerField(default=0, help_text="Calories per serving")
    nutrition_protein = models.PositiveIntegerField(default=0, help_text="Protein in grams per serving")
    nutrition_fat = models.PositiveIntegerField(default=0, help_text="Fat in grams per serving")
    nutrition_carbs = models.PositiveIntegerField(default=0, help_text="Carbohydrates in grams per serving")
    
    # Status & Analytics
    is_draft = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    @property
    def like_count(self):
        return self.likes.count()

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=150)
    amount = models.CharField(max_length=50, blank=True, help_text="e.g., 2, 1/2, or 300")
    unit = models.CharField(max_length=50, blank=True, help_text="e.g., cups, grams, tbsp")

    def __str__(self):
        return f"{self.amount} {self.unit} of {self.name}".strip()

class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='recipes/steps/', blank=True, null=True)
    description = models.TextField()
    tip = models.TextField(blank=True, help_text="Useful tip for this specific cooking step.")

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number} of {self.recipe.title}"

class RecipeComment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"

class RecipeLike(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liked_recipes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.recipe.title}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
