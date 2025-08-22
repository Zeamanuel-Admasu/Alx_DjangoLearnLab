from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, exceptions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer
from .filters import BookFilter

class BookListView(generics.ListAPIView):
    """
    GET /books/ -> list all books (public)

    Supports:
      - Filtering (django-filter):
          ?title=fall
          ?author=1
          ?author_name=achebe
          ?publication_year=1958
          ?publication_year__gte=1950&publication_year__lte=1965
      - Search (DRF SearchFilter):
          ?search=achebe        (matches title or author name)
      - Ordering (DRF OrderingFilter):
          ?ordering=publication_year
          ?ordering=-publication_year
          ?ordering=title
          ?ordering=-publication_year,title  (multi-field)

    Notes:
      - filterset_class centralizes our allowed filters and lookups.
      - search_fields applies full-text-ish icontains to the listed fields.
      - ordering_fields restricts which fields can be sorted on.
    """
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Filtering + search + ordering backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ["title", "author__name"]
    ordering_fields = ["publication_year", "title", "id"]
    ordering = ["title"]  # default



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
