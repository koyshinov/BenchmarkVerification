from django.conf.urls import url

from core.views import index, login_view, logout_view


urlpatterns = [
    url(r'^$', index),
    url(r'^login$', login_view),
    url(r'^logout$', logout_view)
]