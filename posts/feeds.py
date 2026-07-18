from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _
from .models import Post


class LatestPostsFeed(Feed):
    title = "Joan Bono - Blog"
    description = _("Últimas publicaciones del blog de Joan Bono")

    def link(self):
        return reverse('post_list')

    def items(self):
        lang = get_language()[:2] if get_language() else 'es'
        return Post.objects.published_in(lang).order_by('-created_at')[:20]

    def item_title(self, item):
        return item.get_title()

    def item_description(self, item):
        excerpt = item.get_excerpt()
        return excerpt if excerpt else item.get_content()[:300]

    def item_link(self, item):
        return reverse('post_detail', args=[item.slug])

    def item_pubdate(self, item):
        return item.created_at
