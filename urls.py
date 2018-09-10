from django.urls import path
from django.conf.urls import url, include
from . import views
from imdb_recommend.views import *

urlpatterns = [
    # ex: /polls/
    url(r'watchedList', views.watchedList , name='watchedList'),
    url(r'siradaki', views.siradaki , name='getMovie'),
    url(r'search/(?P<title>[\w\-]+)', views.searchMovie , name='searchMovie'),
    url(r'getMovie/(?P<title>[\w\-]+)', views.getMovie , name='getMovie'),
    url(r'movies/check/(?P<title>[\w\-]+)', views.clickwatched, name='watched'),
    url(r'movies', views.main, name='imdb'),

]