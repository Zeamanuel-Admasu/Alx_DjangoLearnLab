from relationship_app.models import Author, Library

from relationship_app.models import Author, Book, Library
from relationship_app.models import Librarian, Library

def books_by_author(author_name):
    author = Author.objects.get(name=author_name)
    return Book.objects.filter(author=author)

# 2. Get all books in a library
def books_in_library(library_name):
    library = Library.objects.get(name=library_name)
    return library.books.all()

# 3. Get the librarian of a library
def get_librarian(library_name):
    library = Library.objects.get(name=library_name)
    return Librarian.objects.get(library=library) 
