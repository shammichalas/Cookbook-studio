from django.urls import path
from . import views

urlpatterns = [
    path('', views.cookbook_list, name='cookbook_list'),
    path('create/', views.cookbook_create, name='cookbook_create'),
    path('<slug:slug>/', views.cookbook_detail, name='cookbook_detail'),
    path('<slug:slug>/edit/', views.cookbook_edit, name='cookbook_edit'),
    path('<slug:slug>/delete/', views.cookbook_delete, name='cookbook_delete'),
    path('<slug:slug>/pdf/', views.generate_pdf, name='generate_pdf'),
]
