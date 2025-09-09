from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    # search & filter
    search_fields = ["title", "content"]
    filterset_fields = ["author"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """
        GET  /api/posts/{id}/comments/   -> list comments for this post
        POST /api/posts/{id}/comments/   -> create comment on this post
        """
        post = self.get_object()
        if request.method.lower() == "get":
            qs = post.comments.select_related("author").all()
            page = self.paginate_queryset(qs)
            ser = CommentSerializer(page or qs, many=True)
            return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

        # POST create comment
        ser = CommentSerializer(data=request.data)
        ser.is_valid(lexcept:=False)  # DRF 3.16 supports raise_exception kw only; keeping explicit check
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save(post=post, author=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("author", "post").all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    # allow list/filter all comments, and inline create if not using nested route
    filterset_fields = ["post", "author"]
    ordering_fields = ["created_at", "updated_at"]

    def perform_create(self, serializer):
        """
        When creating via /api/comments/ directly, require 'post' in payload.
        Author is always the current user.
        """
        serializer.save(author=self.request.user)
