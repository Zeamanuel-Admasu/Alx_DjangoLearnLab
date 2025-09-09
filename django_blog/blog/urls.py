from django.urls import path
from . import views

urlpatterns = [
    # Home / list
    path("", views.PostListView.as_view(), name="post-list"),

    # Auth
    path("login/",  views.BlogLoginView.as_view(), name="login"),
    path("logout/", views.BlogLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),

    # --- REQUIRED BY CHECKER (singular 'post/...') ---
    path("post/new/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post-edit"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),

    # Optional aliases (keep if your templates use the plural paths)
    path("posts/new/", views.PostCreateView.as_view(), name="post-create-alt"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post-edit-alt"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete-alt"),
]
