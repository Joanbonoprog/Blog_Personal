from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.utils.translation import get_language, check_for_language
from django.utils.http import url_has_allowed_host_and_scheme
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
    try:
        limit = int(request.GET.get('limit', 3))
    except (TypeError, ValueError):
        limit = 3
    limit = max(1, min(limit, 20))

    posts = (Post.objects.filter(published=True)
             .exclude(**{title_field: ''})
             .prefetch_related('tags')
             .order_by('-created_at')[:limit])
    data = [
        {
            'title': p.get_title(lang),
            'slug': p.slug,
            'excerpt': p.get_excerpt(lang),
            'created_at': p.created_at.strftime('%Y-%m-%d'),
            'url': f'/blog/{p.slug}/',
            'tags': [{'name': t.name, 'slug': t.slug, 'color': t.color} for t in p.tags.all()],
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


@require_POST
def set_language(request):
    """
    Minimal replacement for django.views.i18n.set_language.

    We don't use i18n_patterns (no language prefix in URLs), so Django's
    built-in view is unnecessary here and actively harmful: it calls
    translate_url(), which runs resolve() on the full 'next' URL (including
    the /blog prefix added by FORCE_SCRIPT_NAME) and then reverse()s it
    again, adding /blog a second time and producing /blog/blog/... 404s.
    This view just sets the language cookie and redirects, without that
    URL-translation step.
    """
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = '/'

    response = HttpResponseRedirect(next_url)
    lang_code = request.POST.get('language')
    if lang_code and check_for_language(lang_code):
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
    return response
