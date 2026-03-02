from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#6366f1', help_text='Color hex, e.g. #6366f1')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Post(models.Model):
    slug = models.SlugField(unique=True)

    title_es = models.CharField(max_length=200, blank=True)
    excerpt_es = models.TextField(blank=True)
    content_es = models.TextField(blank=True)

    title_en = models.CharField(max_length=200, blank=True)
    excerpt_en = models.TextField(blank=True)
    content_en = models.TextField(blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _active_lang(self, lang):
        if lang is None:
            from django.utils.translation import get_language
            active = get_language()
            return active[:2] if active else 'es'
        return lang

    def get_title(self, lang=None):
        return getattr(self, f'title_{self._active_lang(lang)}', '')

    def get_excerpt(self, lang=None):
        return getattr(self, f'excerpt_{self._active_lang(lang)}', '')

    def get_content(self, lang=None):
        return getattr(self, f'content_{self._active_lang(lang)}', '')

    def is_available_in(self, lang):
        return bool(getattr(self, f'title_{lang}', ''))

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.title_es or self.title_en
            self.slug = slugify(base)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_es or self.title_en or self.slug

    class Meta:
        ordering = ['-created_at']
