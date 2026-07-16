from django.test import TestCase
from django.urls import reverse
from posts.models import Post


class PostDetailViewTests(TestCase):
    def setUp(self):
        self.post_published = Post.objects.create(
            title_es="Post Publicado",
            content_es="Contenido del post",
            slug="post-publicado",
            published=True,
        )
        self.post_unpublished = Post.objects.create(
            title_es="Post No Publicado",
            slug="post-no-publicado",
            published=False,
        )
        self.post_es_only = Post.objects.create(
            title_es="Solo ES",
            slug="solo-es",
            published=True,
        )

    def test_published_post_returns_200(self):
        response = self.client.get(reverse("post_detail", args=[self.post_published.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post Publicado")
        self.assertContains(response, "Contenido del post")

    def test_unpublished_post_returns_404(self):
        response = self.client.get(reverse("post_detail", args=[self.post_unpublished.slug]))
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_slug_returns_404(self):
        response = self.client.get(reverse("post_detail", args=["no-existe"]))
        self.assertEqual(response.status_code, 404)

    def test_post_not_available_in_active_language_returns_404(self):
        response = self.client.get(
            reverse("post_detail", args=[self.post_es_only.slug]),
            HTTP_ACCEPT_LANGUAGE="en",
        )
        self.assertEqual(response.status_code, 404)

    def test_post_available_in_active_language_returns_200(self):
        response = self.client.get(
            reverse("post_detail", args=[self.post_es_only.slug]),
            HTTP_ACCEPT_LANGUAGE="es",
        )
        self.assertEqual(response.status_code, 200)
