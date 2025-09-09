# blog/urls.py
from django.urls import path
from . import views


urlpatterns = [
    # Home (from Task 0)
    path("", views.home, name="post-list"),

    # Auth
    path("login/",  views.BlogLoginView.as_view(), name="login"),
    path("logout/", views.BlogLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),

    # Temporary stub (remove/replace in Task 2)
    path("posts/new/", views.post_create_stub, name="post-create"),
]
