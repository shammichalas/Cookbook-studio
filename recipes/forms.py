from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient, RecipeStep, RecipeComment, Category, Tag

class RecipeForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a Category",
        widget=forms.Select(attrs={'class': 'form-select select-mag'})
    )
    
    tags_input = forms.CharField(
        required=False,
        label="Tags (comma-separated)",
        help_text="Enter tags separated by commas (e.g. Italian, Pasta, Dinner)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Summer, Dessert, Healthy'})
    )

    class Meta:
        model = Recipe
        fields = [
            'title', 'cover_image', 'category', 'prep_time', 'cook_time',
            'servings', 'difficulty', 'description', 'chef_notes',
            'nutrition_calories', 'nutrition_protein', 'nutrition_fat', 'nutrition_carbs', 'is_draft'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Discover a Recipe Title...'}),
            'prep_time': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cook_time': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'servings': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'chef_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Chef tips and notes...'}),
            'nutrition_calories': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'nutrition_protein': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'nutrition_fat': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'nutrition_carbs': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_draft': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ", ".join([t.name for t in self.instance.tags.all()])

    def save(self, commit=True):
        recipe = super().save(commit=False)
        if commit:
            recipe.save()
            # Handle tags
            recipe.tags.clear()
            tags_str = self.cleaned_data.get('tags_input', '')
            if tags_str:
                for tag_name in [t.strip() for t in tags_str.split(',') if t.strip()]:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    recipe.tags.add(tag)
        return recipe

# Formsets for dynamic rows
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    fields=('amount', 'unit', 'name'),
    extra=1,
    can_delete=True,
    widgets={
        'amount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2, 1/2'}),
        'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., cups, grams, tbsp'}),
        'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Flour, Sugar, Tomato'}),
    }
)

RecipeStepFormSet = inlineformset_factory(
    Recipe,
    RecipeStep,
    fields=('step_number', 'image', 'description', 'tip'),
    extra=1,
    can_delete=True,
    widgets={
        'step_number': forms.NumberInput(attrs={'class': 'form-control step-number-field', 'readonly': 'readonly'}),
        'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe this step...'}),
        'tip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional tip for this step...'}),
    }
)

class RecipeCommentForm(forms.ModelForm):
    class Meta:
        model = RecipeComment
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control comment-area', 
                'rows': 3, 
                'placeholder': 'Add to the discussion...'
            }),
            'parent': forms.HiddenInput(),
        }
