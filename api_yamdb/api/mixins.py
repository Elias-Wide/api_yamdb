from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets
from rest_framework.filters import SearchFilter

from api.permissions import (IsAdminOrModeratorOrAuthor,
                             IsAdminOrReadOnly, IsAuthenticated)


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

    def get_permissions(self):
        if self.request.method == 'POST':
            return (IsAuthenticated(),)
        elif self.action in ['partial_update', 'destroy']:
            return (IsAdminOrModeratorOrAuthor(),)
        return (permissions.AllowAny(),)

    @staticmethod
    def get_db_object(db_object_model, object_id):
        return get_object_or_404(db_object_model, id=object_id)
