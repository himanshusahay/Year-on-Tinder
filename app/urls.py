from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login', views.login, name='login'),
	url(r'^landing', views.landing, name='landing'),
	url(r'^(?P<match_id>[0-9]+)/profile/$', views.profile, name='profile'),
	url(r'^(?P<match_id>[0-9]+)/send/$', views.send, name='send'),
	url(r'^(?P<match_id>[0-9]+)/category-select/$', views.line_selector, name='category-select'),
]
