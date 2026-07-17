from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts.views import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom set_language view instead of django.conf.urls.i18n's: see
    # posts.views.set_language for why (avoids /blog/blog/ double-prefix bug).
    path('i18n/setlang/', set_language, name='set_language'),
    path('tinymce/', include('tinymce.urls')),
    path('', include('posts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
