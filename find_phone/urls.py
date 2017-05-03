from django.conf.urls import url
from django.contrib import admin


from . import views

urlpatterns = [
    url(r'^user/$', views.user, name="user"),
    url(r'^friends/$', views.friends, name="friends")
]
