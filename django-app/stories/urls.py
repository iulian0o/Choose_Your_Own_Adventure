from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public browsing
    path('', views.story_list, name='story_list'),
    path('story/<int:story_id>/', views.story_detail, name='story_detail'),
    path('statistics/', views.statistics, name='statistics'),
    
    # Playing
    path('play/<int:story_id>/', views.play_story, name='play_story'),
    path('play/<int:story_id>/page/<int:page_id>/', views.play_page, name='play_page'),
    
    # Authentication
    path('register/', views.register, name='register'),  
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Author tools (login required)
    path('author/', views.author_dashboard, name='author_dashboard'),
    path('author/story/create/', views.simple_story_create, name='story_create'),
    path('author/story/<int:story_id>/delete/', views.story_delete, name='story_delete'),
]