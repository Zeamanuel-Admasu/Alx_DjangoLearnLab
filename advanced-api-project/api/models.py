from django.db import models

class Author(models.Model):
    """
    Author model
    ------------
    Purpose:
      Represents a single author who can have many books (1:N).
    Fields:
      - name: Human-readable author name.
    Relationships:
      - Reverse relation to Book via `books` (see Book.author related_name).
    """
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    """
    Book model
    ----------
    Purpose:
      Represents a book written by an Author.
    Fields:
      - title: Book title (free text).
      - publication_year: Year the book was published (integer).
      - author: FK to Author, realizing a one-to-many relationship
                (one author -> many books).
    Relationships:
      - author: Many-to-one; the `related_name="books"` lets us access
                author.books to get all books for an author, which we’ll
                use in the nested serializer.
    """
    title = models.CharField(max_length=255)
    publication_year = models.PositiveIntegerField()
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.publication_year})"
