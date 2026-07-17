from django import forms
from .models import Cookbook
from recipes.models import Recipe

class CookbookForm(forms.ModelForm):
    class Meta:
        model = Cookbook
        fields = ['title', 'cover_image', 'description', 'recipes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. My Tamil Recipes, Festival Specials'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'A brief introduction to this collection...'}),
            'recipes': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Only show published recipes, and prioritize user's own recipes or show all published recipes
        published_recipes = Recipe.objects.filter(is_draft=False)
        if user:
            self.fields['recipes'].queryset = published_recipes
        else:
            self.fields['recipes'].queryset = published_recipes
        
        # Style individual checkbox elements
        self.fields['recipes'].label = "Select Recipes to Include"
