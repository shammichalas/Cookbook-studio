from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/create/', views.recipe_create, name='recipe_create'),
    path('recipes/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<slug:slug>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipes/<slug:slug>/delete/', views.recipe_delete, name='recipe_delete'),
    path('recipes/<slug:slug>/like/', views.like_recipe, name='like_recipe'),
    path('recipes/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('category/<slug:slug>/', views.category_recipes, name='category_recipes'),
    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/search-autocomplete/', views.autocomplete_search, name='autocomplete_search'),
]
