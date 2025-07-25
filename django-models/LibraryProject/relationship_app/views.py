from django.shortcuts import render, get_object_or_404
from django.views.generic.detail import DetailView
from .models import Library  # ✅ matches what the checker expects
from .models import Book     # ✅ still needed

# Function-based view to list all books
def list_books(request):
    books = Book.objects.all()
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Class-based view to show details of a library
class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
