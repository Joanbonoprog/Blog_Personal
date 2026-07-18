from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language


class TagQuerySet(models.QuerySet):
    def with_published_in(self, lang):
        """Tags that have at least one published post in the given language."""
        return self.filter(
            posts__published=True,
            **{f'posts__title_{lang}__gt': ''},
        ).distinct()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#6366f1', help_text='Color hex, e.g. #6366f1')

    objects = TagQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published=True)

    def with_language(self, lang):
        """Posts whose title exists for the given language."""
        return self.exclude(**{f'title_{lang}': ''})

    def published_in(self, lang):
        return self.published().with_language(lang)

    def years_desc(self, lang):
        return self.published_in(lang).dates('created_at', 'year', order='DESC')

    def months_for_year(self, lang, year):
        return (self.published_in(lang)
                .filter(created_at__year=year)
                .dates('created_at', 'month', order='ASC'))

    def ordered(self, lang, order='newest'):
        title_field = f'title_{lang}'
        if order == 'oldest':
            return self.order_by('created_at')
        if order == 'az':
            return self.order_by(title_field)
        if order == 'za':
            return self.order_by(f'-{title_field}')
        return self.order_by('-created_at')


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

    objects = PostQuerySet.as_manager()

    @staticmethod
    def _active_lang(lang=None):
        if lang is None:
            active = get_language()
            return active[:2] if active else 'es'
        return lang

    def _field_value(self, field, lang):
        return getattr(self, f'{field}_{self._active_lang(lang)}', '')

    def get_title(self, lang=None):
        return self._field_value('title', lang)

    def get_excerpt(self, lang=None):
        return self._field_value('excerpt', lang)

    def get_content(self, lang=None):
        return self._field_value('content', lang)

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
