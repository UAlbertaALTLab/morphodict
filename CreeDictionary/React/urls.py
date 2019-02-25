#from django.urls import path
from django.conf.urls import include, url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='home')
               #path('', views.index ),
]
