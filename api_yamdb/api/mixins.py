from rest_framework.exceptions import MethodNotAllowed


class PutNotAllowedMixin():
    def update(self, instance, validated_data):
        if self.context['request'].method == 'PUT':
            raise MethodNotAllowed(method='PUT')
        return super().update(instance, validated_data)