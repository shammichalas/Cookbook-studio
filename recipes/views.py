from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Recipe, Category, Tag, RecipeIngredient, RecipeStep, RecipeComment, RecipeLike, NewsletterSubscriber
from .forms import RecipeForm, RecipeIngredientFormSet, RecipeStepFormSet, RecipeCommentForm
from users.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    """Homepage rendering luxury magazine sections."""
    featured_recipes = Recipe.objects.filter(is_draft=False).annotate(num_likes=Count('likes')).order_by('-num_likes', '-created_at')[:3]
    latest_recipes = Recipe.objects.filter(is_draft=False).order_by('-created_at')[:6]
    categories = Category.objects.all()[:8]
    
    # Top chefs based on recipe count
    popular_chefs = User.objects.annotate(num_recipes=Count('recipes', filter=Q(recipes__is_draft=False))).order_by('-num_recipes')[:4]
    
    context = {
        'featured_recipes': featured_recipes,
        'latest_recipes': latest_recipes,
        'categories': categories,
        'popular_chefs': popular_chefs,
    }
    return render(request, 'home.html', context)

def recipe_list(request):
    """Search and filter list of recipes."""
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    tag_slug = request.GET.get('tag', '')
    
    recipes = Recipe.objects.filter(is_draft=False)
    
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__name__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()
        
    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)
        
    if difficulty:
        recipes = recipes.filter(difficulty=difficulty)
        
    if tag_slug:
        recipes = recipes.filter(tags__slug=tag_slug)

    context = {
        'recipes': recipes,
        'query': query,
        'categories': Category.objects.all(),
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'selected_tag': tag_slug,
    }
    return render(request, 'recipes/recipe_list.html', context)

def category_recipes(request, slug):
    """Filter recipes by a specific category."""
    category = get_object_or_404(Category, slug=slug)
    recipes = Recipe.objects.filter(category=category, is_draft=False)
    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'selected_category': slug,
        'categories': Category.objects.all(),
        'category_name': category.name,
    })

def recipe_detail(request, slug):
    """Detailed recipe layout: view counting, comments, related recipes."""
    recipe = get_object_or_404(Recipe, slug=slug)
    
    # Only allow draft viewing for authors/admins
    if recipe.is_draft and recipe.author != request.user and not request.user.is_staff:
        messages.error(request, "This recipe is a draft.")
        return redirect('home')

    # Increment view count
    recipe.view_count += 1
    recipe.save(update_fields=['view_count'])
    
    comments = recipe.comments.filter(parent=None).prefetch_related('replies')
    comment_form = RecipeCommentForm()
    
    # Related recipes (same category, excluding current, limit 4)
    related_recipes = Recipe.objects.filter(
        category=recipe.category, 
        is_draft=False
    ).exclude(id=recipe.id)[:4]
    
    # If not enough category-related, backfill with newest
    if len(related_recipes) < 4:
        extra_count = 4 - len(related_recipes)
        more_recipes = Recipe.objects.filter(is_draft=False).exclude(
            id__in=[recipe.id] + [r.id for r in related_recipes]
        )[:extra_count]
        related_recipes = list(related_recipes) + list(more_recipes)

    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = RecipeLike.objects.filter(recipe=recipe, user=request.user).exists()

    context = {
        'recipe': recipe,
        'comments': comments,
        'comment_form': comment_form,
        'related_recipes': related_recipes,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'recipes/recipe_detail.html', context)

@login_required
def recipe_create(request):
    """Handles adding a recipe with step and ingredient formsets."""
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            
            ingredient_formset = RecipeIngredientFormSet(request.POST, instance=recipe)
            step_formset = RecipeStepFormSet(request.POST, request.FILES, instance=recipe)
            
            if ingredient_formset.is_valid() and step_formset.is_valid():
                # Save formsets and set relations
                form.save() # Commit tags
                ingredient_formset.save()
                step_formset.save()
                
                messages.success(request, "Your recipe was successfully created!")
                return redirect('recipe_detail', slug=recipe.slug)
            else:
                recipe.delete() # Rollback recipe creation on formset error
        else:
            ingredient_formset = RecipeIngredientFormSet(request.POST)
            step_formset = RecipeStepFormSet(request.POST, request.FILES)
    else:
        form = RecipeForm()
        # Initialize forms with 1 empty row
        ingredient_formset = RecipeIngredientFormSet()
        step_formset = RecipeStepFormSet()

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'title': 'Create Recipe'
    })

@login_required
def recipe_edit(request, slug):
    """Handles updating a recipe and its related steps/ingredients."""
    recipe = get_object_or_404(Recipe, slug=slug)
    if recipe.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this recipe.")
        return redirect('recipe_detail', slug=recipe.slug)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredient_formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        step_formset = RecipeStepFormSet(request.POST, request.FILES, instance=recipe)

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            form.save()
            ingredient_formset.save()
            step_formset.save()
            messages.success(request, "Your recipe was updated successfully!")
            return redirect('recipe_detail', slug=recipe.slug)
    else:
        form = RecipeForm(instance=recipe)
        ingredient_formset = RecipeIngredientFormSet(instance=recipe)
        step_formset = RecipeStepFormSet(instance=recipe)

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'recipe': recipe,
        'title': 'Edit Recipe'
    })

@login_required
def recipe_delete(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    if recipe.author != request.user and not request.user.is_staff:
        messages.error(request, "You are not authorized to delete this recipe.")
        return redirect('recipe_detail', slug=recipe.slug)
    
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recipe deleted successfully.")
        return redirect('profile_view', username=request.user.username)
        
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})

@login_required
@require_POST
def like_recipe(request, slug):
    """Endpoint for liking/unliking a recipe."""
    recipe = get_object_or_404(Recipe, slug=slug)
    like, created = RecipeLike.objects.get_or_create(recipe=recipe, user=request.user)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        
    return JsonResponse({
        'liked': liked,
        'like_count': recipe.like_count
    })

@require_POST
def subscribe_newsletter(request):
    """Newsletter subscription POST endpoint."""
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Please provide a valid email.'})
    
    sub, created = NewsletterSubscriber.objects.get_or_create(email=email)
    if not created:
        return JsonResponse({'status': 'info', 'message': 'You are already subscribed!'})
        
    return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing to Cookbook Studio!'})

def autocomplete_search(request):
    """Dynamic Search Autocomplete JSON Endpoint."""
    query = request.GET.get('q', '').strip()
    results = []
    if len(query) >= 2:
        # Get matching recipes
        recipes = Recipe.objects.filter(is_draft=False, title__icontains=query)[:5]
        for r in recipes:
            results.append({
                'title': r.title,
                'url': f"/recipes/{r.slug}/",
                'type': 'recipe'
            })
            
        # Get matching categories
        categories = Category.objects.filter(name__icontains=query)[:3]
        for c in categories:
            results.append({
                'title': c.name,
                'url': f"/recipes/?category={c.slug}",
                'type': 'category'
            })

        # Get matching authors
        chefs = User.objects.filter(username__icontains=query)[:3]
        for chef in chefs:
            results.append({
                'title': chef.get_full_name() or chef.username,
                'url': f"/users/{chef.username}/",
                'type': 'chef'
            })

    return JsonResponse({'results': results})

@login_required
@require_POST
def add_comment(request, slug):
    """Handle nesting comment submissions."""
    recipe = get_object_or_404(Recipe, slug=slug)
    form = RecipeCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.recipe = recipe
        comment.author = request.user
        
        # Nested comment parent mapping
        parent_id = request.POST.get('parent')
        if parent_id:
            try:
                parent_comment = RecipeComment.objects.get(id=parent_id)
                comment.parent = parent_comment
            except RecipeComment.DoesNotExist:
                pass
                
        comment.save()
        messages.success(request, "Comment posted successfully.")
        return redirect('recipe_detail', slug=recipe.slug)
        
    messages.error(request, "There was an error posting your comment.")
    return redirect('recipe_detail', slug=recipe.slug)
