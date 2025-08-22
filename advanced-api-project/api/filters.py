import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    """
    Rich filters for the Book list:
      - title (icontains)
      - author (by id)
      - author_name (icontains on related Author.name)
      - publication_year exact / range: gte, lte
    """
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    author = django_filters.NumberFilter(field_name="author_id", lookup_expr="exact")
    author_name = django_filters.CharFilter(field_name="author__name", lookup_expr="icontains")
    publication_year = django_filters.NumberFilter(field_name="publication_year", lookup_expr="exact")
    publication_year__gte = django_filters.NumberFilter(field_name="publication_year", lookup_expr="gte")
    publication_year__lte = django_filters.NumberFilter(field_name="publication_year", lookup_expr="lte")

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "author_name",
            "publication_year",
            "publication_year__gte",
            "publication_year__lte",
        ]
