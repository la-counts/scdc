from django.conf.urls import url, include
#from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.views.i18n import JavaScriptCatalog
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from cms.sitemaps import CMSSitemap
from rest_framework import routers
from ckeditor_uploader import views as ckviews
from django.views.generic import RedirectView
from django.contrib.auth.views import password_reset #PasswordResetView

from . import tasks #to enable cron tasks
from . import views
from .views.comments import CommentViewSet
from apps.profiles.views import UserViewSet
from apps.focus.views import ConceptViewSet

router = routers.DefaultRouter()
#router.register(r'comments', CommentViewSet)
router.register(r'users', UserViewSet)
router.register(r'concepts', ConceptViewSet)


urlpatterns = [
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^accounts/register/$', views.register, name='registration_register'),
    url(r'^accounts/password/reset/$', password_reset,
        {'email_template_name': 'registration/password_reset_email.txt',
         'html_email_template_name': 'registration/password_reset_email.html',
         'post_reset_redirect': '/accounts/password/reset/done/'},
        name='password_reset'),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^activity/', include('actstream.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^badgify/', include('badgify.urls')),
    url(r'^catalog/', include('apps.datasets.urls', namespace='datasets')),
    url(r'^ckeditor/upload/', login_required(ckviews.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', never_cache(login_required(ckviews.browse)), name='ckeditor_browse'),
    url(r'^comments/', include('django_comments_xtd.urls')),
    #TODO rename app?
    url(r'^taxonomy/', include('apps.focus.urls', namespace='focus')),
    url(r'^accounts/', include('apps.profiles.urls')),
    url(r'^search/', include('haystack.urls')),
    #url(r'^search/', RedirectView.as_view(url='/catalog/search/')),
    url(r'^stories/', include('apps.stories.urls', namespace='stories')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),
    #url(r'^flag/', include('flag.urls')),

    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),
    url(r'^styleguide/$', views.styleguide, name='styleguide'),
    url(r'^404/$', views.page_not_found),
    url(r'^500/$', views.server_error),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include('djangocms_forms.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#if settings.STATIC_URL.startswith('/'):
#    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]

#cms urls always goes last!
urlpatterns += [
    url(r'^', include('cms.urls')),
]
