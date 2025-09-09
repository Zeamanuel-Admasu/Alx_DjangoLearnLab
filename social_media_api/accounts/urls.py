from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),  # ← trailing slash
    path("login/", views.login, name="login"),          # ← trailing slash
    path("profile/", views.profile, name="profile"),
]
