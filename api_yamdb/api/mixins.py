from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, permissions
from rest_framework.filters import SearchFilter

from api.permissions import IsStaffOrAuthorOrReadOnly, IsAdminOrReadOnly


class PutNotAllowedMixin():
    http_method_names = ['get', 'head', 'post', 'delete', 'patch', 'options']


class CategoryGenreMixin(
    PutNotAllowedMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class ReviewCommentMixin(PutNotAllowedMixin, viewsets.ModelViewSet):
    permission_classes = (IsStaffOrAuthorOrReadOnly,)

    @staticmethod
    def get_db_object(db_object_model, object_id, title=None):
        if title:
            get_object_or_404(db_object_model, id=object_id, title=title)
        return get_object_or_404(db_object_model, id=object_id)
