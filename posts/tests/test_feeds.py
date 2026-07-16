from django.test import TestCase
from django.urls import reverse
from posts.models import Post


class RssFeedTests(TestCase):
    def setUp(self):
        self.post_published = Post.objects.create(
            title_es="Post Publicado",
            excerpt_es="Resumen",
            slug="post-publicado",
            published=True,
        )
        self.post_unpublished = Post.objects.create(
            title_es="No publicado", slug="no-publicado", published=False
        )
        self.post_en_only = Post.objects.create(
            title_en="English Only", slug="english-only", published=True
        )

    def test_feed_returns_200(self):
        response = self.client.get(reverse("rss_feed"))
        self.assertEqual(response.status_code, 200)

    def test_feed_content_type_is_rss(self):
        response = self.client.get(reverse("rss_feed"))
        self.assertIn("rss", response["Content-Type"])

    def test_feed_includes_published_posts_in_active_language(self):
        response = self.client.get(reverse("rss_feed"))
        content = response.content.decode()
        self.assertIn("Post Publicado", content)

    def test_feed_excludes_unpublished_posts(self):
        response = self.client.get(reverse("rss_feed"))
        content = response.content.decode()
        self.assertNotIn("No publicado", content)

    def test_feed_excludes_posts_not_available_in_language(self):
        response = self.client.get(reverse("rss_feed"))
        content = response.content.decode()
        self.assertNotIn("English Only", content)

    def test_feed_limits_to_20_items(self):
        for i in range(25):
            Post.objects.create(
                title_es=f"Post {i}", slug=f"post-{i}", published=True
            )
        response = self.client.get(reverse("rss_feed"))
        content = response.content.decode()
        self.assertEqual(content.count("<item>"), 20)
