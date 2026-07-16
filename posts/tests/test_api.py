import json
from django.test import TestCase
from django.urls import reverse
from posts.models import Post


class RecentPostsApiTests(TestCase):
    def setUp(self):
        for i in range(5):
            Post.objects.create(
                title_es=f"Post {i}",
                excerpt_es=f"Resumen {i}",
                slug=f"post-{i}",
                published=True,
            )
        self.unpublished = Post.objects.create(
            title_es="No publicado", slug="no-publicado", published=False
        )

    def test_returns_200_and_json(self):
        response = self.client.get(reverse("recent_posts"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_returns_max_3_posts(self):
        response = self.client.get(reverse("recent_posts"))
        data = json.loads(response.content)
        self.assertEqual(len(data["posts"]), 3)

    def test_excludes_unpublished_posts(self):
        response = self.client.get(reverse("recent_posts"))
        data = json.loads(response.content)
        slugs = [p["slug"] for p in data["posts"]]
        self.assertNotIn("no-publicado", slugs)

    def test_post_structure(self):
        response = self.client.get(reverse("recent_posts"))
        data = json.loads(response.content)
        post = data["posts"][0]
        self.assertIn("title", post)
        self.assertIn("slug", post)
        self.assertIn("excerpt", post)
        self.assertIn("created_at", post)
        self.assertIn("url", post)
