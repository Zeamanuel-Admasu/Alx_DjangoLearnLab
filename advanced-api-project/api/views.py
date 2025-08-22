from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, exceptions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters import rest_framework  # <-- required import
from .models import Book
from .serializers import BookSerializer
from .filters import BookFilter


class BookListView(generics.ListAPIView):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Filtering + search + ordering backends
    filter_backends = [
        rest_framework.DjangoFilterBackend,  # <-- accessed through the alias
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = BookFilter
    search_fields = ["title", "author__name"]
    ordering_fields = ["publication_year", "title", "id"]
    ordering = ["title"]




class BookDetailView(generics.RetrieveAPIView):
    """
    GET /books/<pk>/ -> retrieve a single book
    """
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class _LookupByIdMixin:
    """
    Allow finding the object via:
      - path param: /books/<pk>/update/ or /books/<pk>/delete/
      - query param: /books/update?id=<pk> or /books/delete?id=<pk>
      - request body: {"id": <pk>}
    """
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_object(self):
        qs = self.get_queryset()
        pk = (
            self.kwargs.get(self.lookup_url_kwarg)
            or self.request.query_params.get("id")
            or self.request.data.get("id")
        )
        if pk is None:
            raise exceptions.ValidationError(
                {"id": "Provide the book ID via path, ?id=, or body."}
            )
        return get_object_or_404(qs, pk=pk)


class BookCreateView(generics.CreateAPIView):
    """
    POST /books/create/ -> create a book (auth required)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class BookUpdateView(_LookupByIdMixin, generics.UpdateAPIView):
    """
    PUT/PATCH /books/<pk>/update/  OR  /books/update[?id=]  (auth required)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.save()


class BookDeleteView(_LookupByIdMixin, generics.DestroyAPIView):
    """
    DELETE /books/<pk>/delete/  OR  /books/delete[?id=]  (auth required)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
