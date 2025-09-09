from rest_framework import serializers
from .models import Post, Comment
from rest_framework import serializers
from .models import Post, Comment, Like   # ← add Like

class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)  # ← add

    class Meta:
        model = Post
        fields = ("id", "author", "author_username", "title", "content",
                  "created_at", "updated_at", "comments_count", "likes_count")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "author_username", "title", "content",
                  "created_at", "updated_at", "comments_count")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "author_username", "content",
                  "created_at", "updated_at")
        read_only_fields = ("post",)  # when using nested create via /posts/{id}/comments/
