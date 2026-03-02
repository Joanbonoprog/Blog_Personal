from django.contrib import admin
from tinymce.widgets import TinyMCE
from django import forms
from .models import Post, Tag


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(mce_attrs={
        'skin': 'oxide-dark',
        'content_css': 'dark',
    }))

    class Meta:
        model = Post
        fields = '__all__'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'published', 'created_at')
    list_filter = ('published', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
