from relationship_app.models import Author, Library


def books_by_author(author_name):
    author = Author.objects.get(name=author_name)
    return author.books.all()


def books_in_library(library_name):
    library = Library.objects.get(name=library_name)
    return library.books.all()


def get_librarian(library_name):
    library = Library.objects.get(name=library_name)
    return library.librarian
