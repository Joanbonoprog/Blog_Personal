from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.utils.translation import get_language, check_for_language
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.paginator import Paginator
from django.db.models import Q, Count
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

    # Responsive page size: 5 rows per breakpoint (cookie set by JS from viewport width)
    try:
        per_page = int(request.COOKIES.get('posts_per_page', 15))
    except (TypeError, ValueError):
        per_page = 15
    allowed_per_page = {5, 10, 15, 20, 25}
    if per_page not in allowed_per_page:
        per_page = 15

    paginator = Paginator(posts, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))

    get_params = request.GET.copy()
    get_params.pop('page', None)
    query_params_without_page = get_params.urlencode()

    all_years = (Post.objects.filter(published=True)
                 .exclude(**{title_field: ''})
                 .dates('created_at', 'year', order='DESC'))

    all_months = None
    if year:
        all_months = (Post.objects.filter(published=True, created_at__year=year)
                      .exclude(**{title_field: ''})
                      .dates('created_at', 'month', order='ASC'))

    return render(request, 'posts/list.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'query_params_without_page': query_params_without_page,
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
    title_field = f'title_{lang}'
    post = get_object_or_404(Post, slug=slug, published=True)
    if not post.is_available_in(lang):
        raise Http404

    base_qs = Post.objects.filter(published=True).exclude(**{title_field: ''})

    # Related posts: share tags with current post, ordered by most shared tags, then most recent.
    post_tag_ids = list(post.tags.values_list('id', flat=True))
    if post_tag_ids:
        related_posts = (
            base_qs.filter(tags__id__in=post_tag_ids)
            .exclude(pk=post.pk)
            .annotate(shared_tags=Count('tags', filter=Q(tags__id__in=post_tag_ids), distinct=True))
            .order_by('-shared_tags', '-created_at')
            .distinct()[:3]
        )
    else:
        related_posts = Post.objects.none()

    # Previous and next posts by creation date (chronologically adjacent).
    prev_post = base_qs.filter(created_at__lt=post.created_at).order_by('-created_at').first()
    next_post = base_qs.filter(created_at__gt=post.created_at).order_by('created_at').first()

    return render(request, 'posts/detail.html', {
        'post': post,
        'lang': lang,
        'related_posts': related_posts,
        'prev_post': prev_post,
        'next_post': next_post,
    })


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
def robots_txt(request):
    """robots.txt: allow all crawlers and point to the sitemap."""
    sitemap_url = request.build_absolute_uri(reverse('sitemap'))
    return HttpResponse(
        f"User-agent: *\nAllow: /\n\nSitemap: {sitemap_url}\n",
        content_type='text/plain',
    )


@require_GET
def llms_txt(request):
    """llms.txt: public content available to AI crawlers, with post list."""
    lang = get_language()[:2]
    title_field = f'title_{lang}'
    posts = (Post.objects.filter(published=True)
             .exclude(**{title_field: ''})
             .order_by('-created_at'))

    site = request.build_absolute_uri('/')
    sitemap_url = request.build_absolute_uri(reverse('sitemap'))
    rss_url = request.build_absolute_uri(reverse('rss_feed'))

    lines = [
        '# llms.txt',
        '# Joan Bono Blog - Public content for AI crawlers',
        '',
        f'Website: {site}',
        f'Sitemap: {sitemap_url}',
        f'RSS: {rss_url}',
        '',
        'User-agent: *',
        'Allow: /',
        '',
        '# Posts',
    ]
    for post in posts:
        post_url = request.build_absolute_uri(reverse('post_detail', args=[post.slug]))
        lines.append(f'- {post.get_title(lang)}: {post_url}')

    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain')


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
