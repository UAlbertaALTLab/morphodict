"""
Definition of urls for CreeDictionary.
"""
from API import views
from django.conf.urls import include, url
from django.urls import path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = [
    path("", include('React.urls')),
    path("React", include('React.urls')),
    # url(r'^React',include('React.urls')),
    # Examples:
    # url(r'^$', CreeDictionary.views.home, name='home'),
    # url(r'^CreeDictionary/', include('CreeDictionary.CreeDictionary.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    path("Search/", views.search, name="Search"),
    path("Search/<str:queryString>", views.search, name="Search"),
    path("DisplayWord/<str:queryString>", views.displayWord, name="DisplayWord"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
