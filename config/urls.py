import os

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from two_factor.admin import AdminSiteOTPRequired
from two_factor.urls import urlpatterns as two_factor_urls
from posts.views import set_language

# Enable admin 2FA only when ADMIN_2FA_ENABLED=True. Set it to False for the
# first deploy so the initial superuser can log in and set up TOTP, then flip
# it to True and redeploy.
if os.getenv('ADMIN_2FA_ENABLED', 'False') == 'True':
    admin.site.__class__ = AdminSiteOTPRequired

urlpatterns = [
    # two_factor login/setup/backup-code URLs. With FORCE_SCRIPT_NAME='/blog'
    # these appear under /blog/login/, /blog/setup/, etc.
    path('', include(two_factor_urls)),
    path('admin/', admin.site.urls),
    # Custom set_language view instead of django.conf.urls.i18n's: see
    # posts.views.set_language for why (avoids /blog/blog/ double-prefix bug).
    path('i18n/setlang/', set_language, name='set_language'),
    path('tinymce/', include('tinymce.urls')),
    path('', include('posts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
