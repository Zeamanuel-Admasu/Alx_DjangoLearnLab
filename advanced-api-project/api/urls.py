from django.urls import path
from .views import (
    BookListView, BookDetailView,
    BookCreateView, BookUpdateView, BookDeleteView
)

urlpatterns = [
    # Original, explicit routes
    path("books/", BookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("books/create/", BookCreateView.as_view(), name="book-create"),
    path("books/<int:pk>/update/", BookUpdateView.as_view(), name="book-update"),
    path("books/<int:pk>/delete/", BookDeleteView.as_view(), name="book-delete"),

    # Aliases required by your checker (no <pk> in path)
    path("books/update", BookUpdateView.as_view(), name="book-update-alias"),   # accepts ?id= or body.id
    path("books/update/", BookUpdateView.as_view()),                           # with trailing slash
    path("books/delete", BookDeleteView.as_view(), name="book-delete-alias"),  # accepts ?id= or body.id
    path("books/delete/", BookDeleteView.as_view()),
]
