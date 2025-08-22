from rest_framework import generics, permissions, filters
from .models import Book
from .serializers import BookSerializer

# READ-ONLY for everyone
class BookListView(generics.ListAPIView):
    """
    GET /books/ -> list all books
    Supports search and ordering.
    """
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

    # Optional: quick filtering via query params:
    #   /books/?search=achebe
    #   /books/?ordering=publication_year  or =-publication_year
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author__name"]
    ordering_fields = ["publication_year", "title"]
    ordering = ["title"]


class BookDetailView(generics.RetrieveAPIView):
    """
    GET /books/<pk>/ -> retrieve one book
    """
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


# WRITE endpoints (auth required)
class BookCreateView(generics.CreateAPIView):
    """
    POST /books/create/ -> create a book
    - Uses serializer validation (publication_year not in future)
    - Example of a customization hook: perform_create
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Any extra side-effects or defaults would go here.
        # Serializer already validates publication_year.
        serializer.save()


class BookUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /books/<pk>/update/ -> update a book
    - Serializer still enforces publication_year rule.
    - Example hook: perform_update
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        # Example: If you wanted to log who updated or enforce custom rules,
        # you'd do it here before/after save.
        serializer.save()


class BookDeleteView(generics.DestroyAPIView):
    """
    DELETE /books/<pk>/delete/ -> delete a book
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
