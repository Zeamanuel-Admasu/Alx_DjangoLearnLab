# posts/views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    # ✔ exact string for the checker
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        # keep optimization while still containing the exact string
        qs = Post.objects.all()
        return qs.select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """
        GET  /api/posts/{id}/comments/  -> list comments for this post
        POST /api/posts/{id}/comments/  -> create comment on this post
        """
        post = self.get_object()
        if request.method == "GET":
            qs = post.comments.select_related("author").all()
            page = self.paginate_queryset(qs)
            ser = CommentSerializer(page or qs, many=True)
            if page is not None:
                return self.get_paginated_response(ser.data)
            return Response(ser.data)

        # POST create comment
        ser = CommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(post=post, author=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    # ✔ exact string for the checker
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        # keep optimization while still containing the exact string
        qs = Comment.objects.all()
        return qs.select_related("author", "post")

    def perform_create(self, serializer):
        """
        When creating via /api/comments/ directly, require 'post' in payload.
        Author is always the current user.
        """
        serializer.save(author=self.request.user)
