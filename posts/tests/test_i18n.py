from django.test import TestCase, override_settings
from django.urls import reverse


class SetLanguageViewTests(TestCase):
    def test_get_not_allowed(self):
        response = self.client.get(reverse("set_language"))
        self.assertEqual(response.status_code, 405)

    def test_redirects_to_next_and_sets_cookie(self):
        response = self.client.post(
            reverse("set_language"), {"language": "en", "next": "/some-post/"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/some-post/")
        self.assertEqual(response.cookies["django_language"].value, "en")

    def test_invalid_language_still_redirects_without_setting_cookie(self):
        response = self.client.post(
            reverse("set_language"), {"language": "xx", "next": "/some-post/"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("django_language", response.cookies)

    def test_falls_back_to_root_for_unsafe_next(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "en", "next": "https://evil.com/phish"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

    @override_settings(FORCE_SCRIPT_NAME="/blog")
    def test_does_not_duplicate_force_script_name_prefix(self):
        """
        Regression test: Django's built-in django.views.i18n.set_language
        calls translate_url(), which runs resolve() on the full 'next' URL.
        Under FORCE_SCRIPT_NAME='/blog', 'next' already contains the /blog
        prefix (e.g. '/blog/some-post/'), and resolve() (which is unaware
        of SCRIPT_NAME) matches "blog" as a post slug via the catch-all
        <slug:slug>/ pattern. reverse()-ing that match then re-adds the
        forced script prefix, producing '/blog/blog/some-post/'.

        Our custom set_language view (posts.views.set_language) skips
        translate_url entirely, so 'next' must be returned unchanged.
        """
        response = self.client.post(
            reverse("set_language"),
            {"language": "en", "next": "/blog/some-post/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/blog/some-post/")
