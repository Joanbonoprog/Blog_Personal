from django.test import TestCase
from django.urls import reverse
from posts.models import Post


class SitemapTests(TestCase):
    def setUp(self):
        self.post_es = Post.objects.create(
            title_es="Post ES", slug="post-es", published=True
        )
        self.post_en = Post.objects.create(
            title_en="Post EN", slug="post-en", published=True
        )
        self.post_bilingual = Post.objects.create(
            title_es="Bilingüe ES",
            title_en="Bilingual EN",
            slug="post-bilingue",
            published=True,
        )
        self.post_unpublished = Post.objects.create(
            title_es="No publicado", slug="no-publicado", published=False
        )

    def test_sitemap_returns_200_and_xml_content_type(self):
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_sitemap_includes_home_url(self):
        response = self.client.get(reverse("sitemap"))
        content = response.content.decode()
        self.assertIn("<loc>", content)

    def test_sitemap_includes_published_posts(self):
        response = self.client.get(reverse("sitemap"))
        content = response.content.decode()
        self.assertIn("post-es", content)
        self.assertIn("post-en", content)
        self.assertIn("post-bilingue", content)

    def test_sitemap_excludes_unpublished_posts(self):
        response = self.client.get(reverse("sitemap"))
        content = response.content.decode()
        self.assertNotIn("no-publicado", content)

    def test_sitemap_does_not_duplicate_bilingual_post(self):
        response = self.client.get(reverse("sitemap"))
        content = response.content.decode()
        self.assertEqual(content.count("post-bilingue"), 1)
