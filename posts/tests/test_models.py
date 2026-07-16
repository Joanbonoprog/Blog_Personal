from django.test import TestCase
from django.utils import translation
from posts.models import Post, Tag


class TagModelTests(TestCase):
    def test_slug_auto_generated_from_name(self):
        tag = Tag.objects.create(name="Machine Learning")
        self.assertEqual(tag.slug, "machine-learning")

    def test_slug_not_overwritten_if_provided(self):
        tag = Tag.objects.create(name="Machine Learning", slug="ml-custom")
        self.assertEqual(tag.slug, "ml-custom")

    def test_default_color(self):
        tag = Tag.objects.create(name="Python")
        self.assertEqual(tag.color, "#6366f1")

    def test_str_returns_name(self):
        tag = Tag.objects.create(name="Django")
        self.assertEqual(str(tag), "Django")


class PostModelTests(TestCase):
    def test_slug_auto_generated_from_title_es(self):
        post = Post.objects.create(title_es="Mi Primer Post", published=True)
        self.assertEqual(post.slug, "mi-primer-post")

    def test_slug_auto_generated_from_title_en_if_no_es(self):
        post = Post.objects.create(title_en="My First Post", published=True)
        self.assertEqual(post.slug, "my-first-post")

    def test_slug_not_overwritten_if_provided(self):
        post = Post.objects.create(title_es="Título", slug="custom-slug", published=True)
        self.assertEqual(post.slug, "custom-slug")

    def test_get_title_with_explicit_lang(self):
        post = Post.objects.create(
            title_es="Título ES", title_en="Title EN", published=True
        )
        self.assertEqual(post.get_title("es"), "Título ES")
        self.assertEqual(post.get_title("en"), "Title EN")

    def test_get_title_uses_active_language_when_lang_is_none(self):
        post = Post.objects.create(
            title_es="Título ES", title_en="Title EN", published=True
        )
        with translation.override("en"):
            self.assertEqual(post.get_title(), "Title EN")
        with translation.override("es"):
            self.assertEqual(post.get_title(), "Título ES")

    def test_get_excerpt_and_get_content(self):
        post = Post.objects.create(
            title_es="Título",
            excerpt_es="Resumen ES",
            content_es="Contenido ES",
            published=True,
        )
        self.assertEqual(post.get_excerpt("es"), "Resumen ES")
        self.assertEqual(post.get_content("es"), "Contenido ES")

    def test_is_available_in_true_when_title_present(self):
        post = Post.objects.create(title_es="Título", published=True)
        self.assertTrue(post.is_available_in("es"))

    def test_is_available_in_false_when_title_missing(self):
        post = Post.objects.create(title_es="Título", published=True)
        self.assertFalse(post.is_available_in("en"))

    def test_str_fallback_order(self):
        post_es = Post.objects.create(title_es="Solo ES", published=True)
        self.assertEqual(str(post_es), "Solo ES")

        post_en = Post.objects.create(title_en="Only EN", published=True)
        self.assertEqual(str(post_en), "Only EN")

        post_slug_only = Post.objects.create(slug="no-title-post", published=True)
        self.assertEqual(str(post_slug_only), "no-title-post")

    def test_ordering_is_by_created_at_desc(self):
        older = Post.objects.create(title_es="Viejo", published=True)
        newer = Post.objects.create(title_es="Nuevo", published=True)
        posts = list(Post.objects.all())
        self.assertEqual(posts[0].pk, newer.pk)
        self.assertEqual(posts[1].pk, older.pk)
