"""
Definition of urls for CreeDictionary.
"""

from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
               #path('', include('React.urls')),
    
    # Examples:
    # url(r'^$', CreeDictionary.views.home, name='home'),
    # url(r'^CreeDictionary/', include('CreeDictionary.CreeDictionary.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]
