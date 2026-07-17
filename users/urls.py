from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('<str:username>/', views.profile_view, name='profile_view'),
    path('<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
]
