from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from .models import Profile
from .forms import SignUpForm, UserEditForm, ProfileEditForm
from recipes.models import Recipe, RecipeLike
from cookbooks.models import Cookbook
from django.contrib.auth import get_user_model

User = get_user_model()

def signup_view(request):
    """Sign up new users."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Cookbook Studio, {user.first_name or user.username}!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    """Log in existing users."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('home')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    """Log out users."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

def profile_view(request, username):
    """Renders user profile, drafts, favorites, cookbooks, and stats."""
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    
    # Recipes query
    all_recipes = Recipe.objects.filter(author=profile_user)
    published_recipes = all_recipes.filter(is_draft=False)
    drafts = all_recipes.filter(is_draft=True) if request.user == profile_user or request.user.is_staff else Recipe.objects.none()
    
    # Cookbooks
    cookbooks = Cookbook.objects.filter(owner=profile_user)
    
    # Favorite recipes (liked by this user)
    liked_recipe_ids = RecipeLike.objects.filter(user=profile_user).values_list('recipe_id', flat=True)
    favorites = Recipe.objects.filter(id__in=liked_recipe_ids, is_draft=False)
    
    # Statistics calculations
    total_views = published_recipes.aggregate(Sum('view_count'))['view_count__sum'] or 0
    total_likes = sum(recipe.like_count for recipe in published_recipes)
    
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = request.user.profile.follows.filter(id=profile.id).exists()

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'published_recipes': published_recipes,
        'drafts': drafts,
        'cookbooks': cookbooks,
        'favorites': favorites,
        'total_views': total_views,
        'total_likes': total_likes,
        'is_following': is_following,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """Update profile bio and image."""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile_view', username=user.username)
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=profile)
        
    return render(request, 'users/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
@require_POST
def toggle_follow(request, username):
    """Endpoint to follow/unfollow a chef profile."""
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'status': 'error', 'message': 'You cannot follow yourself.'})
        
    user_profile = request.user.profile
    target_profile = target_user.profile
    
    if user_profile.follows.filter(id=target_profile.id).exists():
        user_profile.follows.remove(target_profile)
        followed = False
    else:
        user_profile.follows.add(target_profile)
        followed = True
        
    return JsonResponse({
        'followed': followed,
        'follower_count': target_profile.follower_count
    })
