from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django.utils.translation import get_language
from django.db.models import Q
from django.urls import reverse
from .models import Post, Tag


def post_list(request):
    lang = get_language()[:2]
    title_field = f'title_{lang}'

    posts = Post.objects.filter(published=True).exclude(**{title_field: ''})
    all_tags = Tag.objects.filter(posts__published=True, **{f'posts__title_{lang}__gt': ''}).distinct()

    tag_slug = request.GET.get('tag') or None
    order = request.GET.get('order', 'newest')
    year = request.GET.get('year') or None
    month = request.GET.get('month') or None
    query = (request.GET.get('q') or '').strip()

    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    if year:
        posts = posts.filter(created_at__year=year)
    if month:
        posts = posts.filter(created_at__month=month)
    if query:
        posts = posts.filter(Q(**{f'{title_field}__icontains': query}) | Q(slug__icontains=query))

    if order == 'oldest':
        posts = posts.order_by('created_at')
    elif order == 'az':
        posts = posts.order_by(title_field)
    elif order == 'za':
        posts = posts.order_by(f'-{title_field}')
    else:
        posts = posts.order_by('-created_at')

    all_years = (Post.objects.filter(published=True)
                 .exclude(**{title_field: ''})
                 .dates('created_at', 'year', order='DESC'))

    all_months = None
    if year:
        all_months = (Post.objects.filter(published=True, created_at__year=year)
                      .exclude(**{title_field: ''})
                      .dates('created_at', 'month', order='ASC'))

    return render(request, 'posts/list.html', {
        'posts': posts,
        'all_tags': all_tags,
        'active_tag': tag_slug,
        'order': order,
        'lang': lang,
        'all_years': all_years,
        'all_months': all_months,
        'active_year': year,
        'active_month': month,
        'query': query,
    })


def post_detail(request, slug):
    lang = get_language()[:2]
    post = get_object_or_404(Post, slug=slug, published=True)
    if not post.is_available_in(lang):
        raise Http404
    return render(request, 'posts/detail.html', {'post': post, 'lang': lang})


@require_GET
def recent_posts(request):
    lang = get_language()[:2]
    title_field = f'title_{lang}'
    posts = Post.objects.filter(published=True).exclude(**{title_field: ''})[:3]
    data = [
        {
            'title': p.get_title(lang),
            'slug': p.slug,
            'excerpt': p.get_excerpt(lang),
            'created_at': p.created_at.strftime('%Y-%m-%d'),
            'url': f'/blog/{p.slug}/'
        }
        for p in posts
    ]
    return JsonResponse({'posts': data})


@require_GET
def sitemap_xml(request):
    languages = ['es', 'en']
    entries = [{
        'loc': request.build_absolute_uri(reverse('post_list')),
        'lastmod': None,
        'changefreq': 'daily',
        'priority': '1.0',
    }]

    seen_slugs = set()
    for lang in languages:
        title_field = f'title_{lang}'
        posts = (Post.objects.filter(published=True)
                 .exclude(**{title_field: ''})
                 .order_by('-updated_at'))
        for post in posts:
            if post.slug in seen_slugs:
                continue
            seen_slugs.add(post.slug)
            entries.append({
                'loc': request.build_absolute_uri(reverse('post_detail', args=[post.slug])),
                'lastmod': post.updated_at.strftime('%Y-%m-%d'),
                'changefreq': 'monthly',
                'priority': '0.8',
            })

    return render(request, 'posts/sitemap.xml', {'entries': entries}, content_type='application/xml')
