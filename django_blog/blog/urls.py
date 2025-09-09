# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='post-list'),  # temporary home
]
