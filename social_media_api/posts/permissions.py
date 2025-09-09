from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Read: anyone authenticated (or public, if you later switch permission).
    Write: only the object owner (author).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "author_id", None) == getattr(request.user, "id", None)
