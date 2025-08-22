## DRF Generic Views for Book

### Endpoints
- `GET /books/` — List all books (public)
  - Optional query params: `search=<term>`, `ordering=publication_year|-publication_year|title|-title`
- `GET /books/<pk>/` — Retrieve a single book (public)
- `POST /books/create/` — Create a book (authenticated)
- `PUT|PATCH /books/<pk>/update/` — Update a book (authenticated)
- `DELETE /books/<pk>/delete/` — Delete a book (authenticated)

### Behavior & Customization
- Uses DRF generic class-based views (`ListAPIView`, `RetrieveAPIView`, `CreateAPIView`, `UpdateAPIView`, `DestroyAPIView`).
- Validation: `BookSerializer.validate_publication_year` prevents future years.
- Permissions: read for all, write for authenticated users only.
- Filtering: `SearchFilter` on `title` and `author__name`; `OrderingFilter` on `publication_year` and `title`.
- Hooks:
  - `perform_create` and `perform_update` are provided to add side effects or extra rules if needed.

### Filtering / Search / Ordering (Books)

**Endpoint:** `GET /books/`

**Filtering (django-filter):**
- `?title=<substr>` — icontains on book title
- `?author=<id>` — exact author id
- `?author_name=<substr>` — icontains on related `Author.name`
- `?publication_year=<year>` — exact match
- `?publication_year__gte=<year>&publication_year__lte=<year>` — range

**Search (DRF SearchFilter):**
- `?search=<term>` matches `title` and `author__name`

**Ordering (DRF OrderingFilter):**
- `?ordering=title` | `?ordering=-publication_year` | multi-field: `?ordering=-publication_year,title`

**Notes:**
- Implemented via `BookFilter` (`api/filters.py`) and `BookListView` backends.
- Default ordering is by `title`.
