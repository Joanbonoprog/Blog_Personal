from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Post


def post_list(request):
    posts = Post.objects.filter(published=True)
    return render(request, 'posts/list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    return render(request, 'posts/detail.html', {'post': post})


@require_GET
def recent_posts(request):
    posts = Post.objects.filter(published=True)[:3]
    data = [
        {
            'title': p.title,
            'slug': p.slug,
            'excerpt': p.excerpt,
            'created_at': p.created_at.strftime('%Y-%m-%d'),
            'url': f'/blog/{p.slug}/'
        }
        for p in posts
    ]
    return JsonResponse({'posts': data})
