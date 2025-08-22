from datetime import date
from rest_framework import serializers
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    BookSerializer
    --------------
    Purpose:
      - Serialize/deserialize Book instances.
      - Enforce domain validation on publication_year.
    Fields:
      - id, title, publication_year, author (FK id).
    Validation:
      - publication_year must not be in the future.
    """
    class Meta:
        model = Book
        fields = ["id", "title", "publication_year", "author"]

    def validate_publication_year(self, value: int) -> int:
        """Ensure publication_year is not in the future."""
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                f"publication_year cannot be in the future (>{current_year})."
            )
        return value


class AuthorSerializer(serializers.ModelSerializer):
    """
    AuthorSerializer
    ----------------
    Purpose:
      - Serialize Author with a nested list of their books.
    Fields:
      - id, name, books (nested BookSerializer, read-only).
    Relationship handling:
      - Uses the reverse relation `Author.books` (set by Book.author.related_name)
        to dynamically include all books for an author.
      - We mark `books` as read_only=True to keep nested writes out for now.
        (If you want to support creating/updating books inline,
         override create()/update() to handle nested input.)
    """
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "books"]
