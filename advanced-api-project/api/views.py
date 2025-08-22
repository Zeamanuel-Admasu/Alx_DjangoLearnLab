from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, filters, exceptions
from .models import Book
from .serializers import BookSerializer

class BookListView(generics.ListAPIView):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author__name"]
    ordering_fields = ["publication_year", "title"]
    ordering = ["title"]

class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

class _LookupByIdMixin:
    """Allow finding the object via path <pk>, query ?id=, or request.data['id']."""
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
            raise exceptions.ValidationError({"id": "Provide the book ID via path, ?id=, or body."})
        return get_object_or_404(qs, pk=pk)

class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save()

class BookUpdateView(_LookupByIdMixin, generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_update(self, serializer):
        serializer.save()

class BookDeleteView(_LookupByIdMixin, generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
