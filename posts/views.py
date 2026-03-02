from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Post, Tag


def post_list(request):
    posts = Post.objects.filter(published=True)
    all_tags = Tag.objects.filter(posts__published=True).distinct()

    tag_slug = request.GET.get('tag') or None
    order = request.GET.get('order', 'newest')

    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    if order == 'oldest':
        posts = posts.order_by('created_at')
    elif order == 'az':
        posts = posts.order_by('title')
    elif order == 'za':
        posts = posts.order_by('-title')
    else:
        posts = posts.order_by('-created_at')

    return render(request, 'posts/list.html', {
        'posts': posts,
        'all_tags': all_tags,
        'active_tag': tag_slug,
        'order': order,
    })


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
