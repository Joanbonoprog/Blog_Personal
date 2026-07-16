from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import get_language
from .models import Post


class LatestPostsFeed(Feed):
    title = "Joan Bono - Blog"
    description = "Últimas publicaciones del blog de Joan Bono"

    def link(self):
        return reverse('post_list')

    def items(self):
        lang = get_language()[:2] if get_language() else 'es'
        title_field = f'title_{lang}'
        return (Post.objects.filter(published=True)
                .exclude(**{title_field: ''})
                .order_by('-created_at')[:20])

    def item_title(self, item):
        return item.get_title()

    def item_description(self, item):
        excerpt = item.get_excerpt()
        return excerpt if excerpt else item.get_content()[:300]

    def item_link(self, item):
        return reverse('post_detail', args=[item.slug])

    def item_pubdate(self, item):
        return item.created_at
