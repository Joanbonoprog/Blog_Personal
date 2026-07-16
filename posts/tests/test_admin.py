from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from tinymce.widgets import TinyMCE
from posts.admin import PostAdmin, PostAdminForm, TagAdmin
from posts.models import Post, Tag

User = get_user_model()


class PostAdminFormTests(TestCase):
    def test_content_es_uses_tinymce_widget(self):
        form = PostAdminForm()
        self.assertIsInstance(form.fields["content_es"].widget, TinyMCE)

    def test_content_en_uses_tinymce_widget(self):
        form = PostAdminForm()
        self.assertIsInstance(form.fields["content_en"].widget, TinyMCE)

    def test_content_fields_not_required(self):
        form = PostAdminForm()
        self.assertFalse(form.fields["content_es"].required)
        self.assertFalse(form.fields["content_en"].required)


class PostAdminConfigTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = PostAdmin(Post, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display, ("__str__", "published", "created_at")
        )

    def test_list_filter(self):
        self.assertEqual(self.admin.list_filter, ("published", "tags"))

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            ("title_es", "title_en", "content_es", "content_en"),
        )

    def test_prepopulated_fields(self):
        self.assertEqual(self.admin.prepopulated_fields, {"slug": ("title_es",)})

    def test_filter_horizontal(self):
        self.assertEqual(self.admin.filter_horizontal, ("tags",))

    def test_uses_custom_form(self):
        self.assertEqual(self.admin.form, PostAdminForm)


class TagAdminConfigTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = TagAdmin(Tag, self.site)

    def test_list_display(self):
        self.assertEqual(self.admin.list_display, ("name", "slug"))

    def test_prepopulated_fields(self):
        self.assertEqual(self.admin.prepopulated_fields, {"slug": ("name",)})


class AdminSiteIntegrationTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="testpass123"
        )
        self.client = Client()
        self.client.login(username="admin", password="testpass123")

    def test_post_changelist_accessible(self):
        response = self.client.get(reverse("admin:posts_post_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_post_add_page_accessible(self):
        response = self.client.get(reverse("admin:posts_post_add"))
        self.assertEqual(response.status_code, 200)

    def test_tag_changelist_accessible(self):
        response = self.client.get(reverse("admin:posts_tag_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_post_registered_in_admin(self):
        from django.contrib import admin as django_admin
        self.assertIn(Post, django_admin.site._registry)

    def test_tag_registered_in_admin(self):
        from django.contrib import admin as django_admin
        self.assertIn(Tag, django_admin.site._registry)
