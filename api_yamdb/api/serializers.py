import string
import secrets

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, MethodNotAllowed

from api.constants import MAX_SCORE_VALUE, MIN_SCORE_VALUE
from api.mixins import PutNotAllowedMixin
from reviews.models import (
    Category,
    Comment,
    CustomUser,
    Genre,
    Review,
    Title
)


def generate_confirmation_code(length=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_confirmation_email(email, confirmation_code):
    send_mail(subject='Confirmation Code',
              message=f'Your confirmation code is: {confirmation_code}',
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[email])


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username')

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        existing_user = CustomUser.objects.filter(email=email, username=username).first()
        if existing_user:
            return attrs
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email must be unique.")
        if CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username must be unique.")
        return attrs

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        existing_user = CustomUser.objects.filter(email=email, username=username).first()
        confirmation_code = generate_confirmation_code()
        if existing_user:
            existing_user.confirmation_code = confirmation_code
            existing_user.save()
            send_confirmation_email(email, confirmation_code)
            return existing_user
        user = CustomUser.objects.create_user(email=email, username=username)
        user.confirmation_code = confirmation_code
        user.save()
        send_confirmation_email(email, confirmation_code)
        return user


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=6, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'confirmation_code')


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate(self, attrs):
        if self.context['request'].method == 'PATCH':
            if not attrs.get('username') or not attrs.get('email'):
                raise ValidationError(
                    'username and email are required fields for PATCH requests.'
                )
        return attrs


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleCreateSerializer(PutNotAllowedMixin, serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=False
    )

    class Meta:
        model = Title
        fields = '__all__'

    # def update(self, instance, validated_data):
    #     if self.context['request'].method == 'PUT':
    #         raise MethodNotAllowed(method='PUT')
    #     return super().update(instance, validated_data)

class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def update(self, instance, validated_data):
        if self.context['request'].method == 'PUT':
            raise MethodNotAllowed(method='PUT')
        return super().update(instance, validated_data)

    def validate_score(self, value):
        if not (MIN_SCORE_VALUE <= value <= MAX_SCORE_VALUE):
            raise serializers.ValidationError(
                'The score must be in the range from 1 to 10!'
            )
        return value

    def validate(self, data):

        title = get_object_or_404(
            Title, id=self.context['view'].kwargs['title_id']
        )
        user = self.context['request'].user
        if (
            Review.objects.filter(title=title, author=user).exists()
            and self.context['request'].method == 'POST'
        ):
            raise serializers.ValidationError(
                'You can leave only one review for a title!'
            )
        return data


class CommentSerializer(PutNotAllowedMixin, serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment

    # def update(self, instance, validated_data):
    #     if self.context['request'].method == 'PUT':
    #         raise MethodNotAllowed(method='PUT')
    #     return super().update(instance, validated_data)
