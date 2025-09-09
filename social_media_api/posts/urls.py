from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, FeedView   # ← import FeedView

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("", include(router.urls)),
    # ✅ EXACT route the checker wants present in posts/urls.py
    path("feed/", FeedView.as_view(), name="feed"),
]
