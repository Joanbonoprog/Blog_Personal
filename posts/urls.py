from django.urls import path
from . import views
from .feeds import LatestPostsFeed

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('rss.xml', LatestPostsFeed(), name='rss_feed'),
    path('api/recent/', views.recent_posts, name='recent_posts'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
