from django.urls import path
from . import views

urlpatterns = [
    # already present...
    path("", views.PostListView.as_view(), name="post-list"),
    path("login/",  views.BlogLoginView.as_view(), name="login"),
    path("logout/", views.BlogLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),

    # posts (Task 2)
    path("post/new/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post-edit"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),

    # comments (Task 3) — primary (singular base)
    path("post/<int:post_id>/comments/new/", views.CommentCreateView.as_view(), name="comment-create"),
    path("comment/<int:pk>/update/", views.CommentUpdateView.as_view(), name="comment-edit"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment-delete"),

    # optional aliases (plural base)
    path("posts/<int:post_id>/comments/new/", views.CommentCreateView.as_view(), name="comment-create-alt"),
    path("comments/<int:pk>/edit/", views.CommentUpdateView.as_view(), name="comment-edit-alt"),
    path("comments/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment-delete-alt"),
]
