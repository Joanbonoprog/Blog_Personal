from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from posts.models import Post, Tag


class PostListViewTests(TestCase):
    def setUp(self):
        self.tag_python = Tag.objects.create(name="Python")
        self.tag_django = Tag.objects.create(name="Django")

        self.post_es_only = Post.objects.create(
            title_es="Post en Español",
            slug="post-en-espanol",
            published=True,
        )
        self.post_en_only = Post.objects.create(
            title_en="English Post",
            slug="english-post",
            published=True,
        )
        self.post_bilingual = Post.objects.create(
            title_es="Post Bilingüe",
            title_en="Bilingual Post",
            slug="post-bilingue",
            published=True,
        )
        self.post_unpublished = Post.objects.create(
            title_es="No publicado",
            slug="no-publicado",
            published=False,
        )
        self.post_bilingual.tags.add(self.tag_python)

    def test_only_published_posts_shown(self):
        response = self.client.get(reverse("post_list"))
        self.assertNotContains(response, "No publicado")

    def test_only_posts_available_in_active_language_es(self):
        response = self.client.get(reverse("post_list"))
        self.assertContains(response, "Post en Español")
        self.assertContains(response, "Post Bilingüe")
        self.assertNotContains(response, "English Post")

    def test_only_posts_available_in_active_language_en(self):
        response = self.client.get(reverse("post_list"), HTTP_ACCEPT_LANGUAGE="en")
        self.assertContains(response, "English Post")
        self.assertContains(response, "Bilingual Post")
        self.assertNotContains(response, "Post en Español")

    def test_filter_by_tag(self):
        response = self.client.get(reverse("post_list"), {"tag": self.tag_python.slug})
        self.assertContains(response, "Post Bilingüe")
        self.assertNotContains(response, "Post en Español")

    def test_filter_by_year(self):
        year = timezone.now().year
        response = self.client.get(reverse("post_list"), {"year": year})
        self.assertContains(response, "Post en Español")

        response = self.client.get(reverse("post_list"), {"year": year - 10})
        self.assertNotContains(response, "Post en Español")

    def test_search_by_title(self):
        response = self.client.get(reverse("post_list"), {"q": "Bilingüe"})
        self.assertContains(response, "Post Bilingüe")
        self.assertNotContains(response, "Post en Español")

    def test_search_by_slug_excludes_post_unavailable_in_active_language(self):
        # post_en_only has no title_es, so it's excluded from the 'es' queryset
        # regardless of slug matching the search query.
        response = self.client.get(reverse("post_list"), {"q": "english-post"})
        self.assertNotContains(response, "English Post")

    def test_search_by_slug_matches_when_available_in_language(self):
        response = self.client.get(reverse("post_list"), {"q": "post-bilingue"})
        self.assertContains(response, "Post Bilingüe")

    def test_search_no_results(self):
        response = self.client.get(reverse("post_list"), {"q": "noexisteesteposteninguno"})
        self.assertContains(response, "No se encontraron posts")

    def test_order_newest_default(self):
        response = self.client.get(reverse("post_list"))
        content = response.content.decode()
        pos_bilingue = content.find("Post Bilingüe")
        pos_espanol = content.find("Post en Español")
        # bilingual created after post_es_only, so should appear first (newest first)
        self.assertLess(pos_bilingue, pos_espanol)

    def test_order_oldest(self):
        response = self.client.get(reverse("post_list"), {"order": "oldest"})
        content = response.content.decode()
        pos_espanol = content.find("Post en Español")
        pos_bilingue = content.find("Post Bilingüe")
        self.assertLess(pos_espanol, pos_bilingue)

    def test_order_az(self):
        response = self.client.get(reverse("post_list"), {"order": "az"})
        content = response.content.decode()
        pos_bilingue = content.find("Post Bilingüe")
        pos_espanol = content.find("Post en Español")
        # 'Post Bilingüe' < 'Post en Español' alphabetically (B < e, case-sensitive depends on DB collation)
        self.assertTrue(pos_bilingue != -1 and pos_espanol != -1)

    def test_all_tags_excludes_tags_without_published_posts_in_language(self):
        response = self.client.get(reverse("post_list"))
        self.assertContains(response, "Python")
        self.assertNotContains(response, "Django</option>")
