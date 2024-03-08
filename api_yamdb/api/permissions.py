from rest_framework import permissions


class IsAdminOrModeratorOrAuthor(permissions.BasePermission):
    """
    Allows access to admins, moderators, or the author of the object.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
                return True
        return (
                request.user.role == 'admin' or
                request.user.role == 'moderator' or
                obj.author == request.user
        )


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Allows access only to authenticated users who own the object,
    or read-only access to other users.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsModeratorOrReadOnly(permissions.BasePermission):
    """
    Allows access to moderators to edit and delete any content,
    read-only access to others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role == 'moderator' 
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'moderator'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows access to admins to manage content,
    read-only access to others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role == 'admin' 
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'admin'

class IsAdmin(permissions.BasePermission):
    """
    Allows access to admins to manage content,
    read-only access to others.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'


# class ReadOnly(permissions.BasePermission):
#
#     def has_permission(self, request, view):
#         return request.method in permissions.SAFE_METHODS
#
#
# class AuthorOrReadOnly(permissions.BasePermission):
#
#     def has_permission(self, request, view):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.is_authenticated
#         )
#
#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or obj.author == request.user
#         )
#
#
# class Moderator(permissions.BasePermission):
#
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         if request.user.is_authenticated:
#             return True
#         return False
#
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         if request.user.is_authenticated:
#             return request.user.role == 'moderator'
#         return False
