# LibraryProject

This Django project implements custom user models with group-based permissions.

## Permissions & Groups Setup

We use Django's built-in permission system to restrict access based on user roles.

### Custom Permissions (defined in `Book` model)

- `can_view`: Allows viewing the list of books.
- `can_create`: Allows creating new books.
- `can_edit`: Allows editing existing books.
- `can_delete`: Allows deleting books.

### Groups

Created and configured via Django Admin:
- **Viewers**: Has `can_view` permission.
- **Editors**: Has `can_view`, `can_create`, `can_edit`.
- **Admins**: Has all permissions including `can_delete`.

### Views

In `views.py`, the `@permission_required` decorator is used to restrict access.

Example:
```python
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
    ...
