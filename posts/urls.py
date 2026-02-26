from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('api/recent/', views.recent_posts, name='recent_posts'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
