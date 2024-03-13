import re
import secrets
import string

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title
from api.constants import MAX_SCORE_VALUE, MIN_SCORE_VALUE


def generate_confirmation_code(length=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_confirmation_email(email, confirmation_code):
    send_mail(subject='Confirmation Code',
              message=f'Your confirmation code is: {confirmation_code}',
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[email])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']
        self.fields['username'] = serializers.CharField()
        self.fields['confirmation_code'] = serializers.CharField(max_length=6,
                                                                 required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(CustomUser, username=username)
        if confirmation_code != user.confirmation_code:
            raise ValidationError('Incorrect confirmation code')
        return attrs


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username')

    def get_existing_user():
        pass

    def validate_email(self, value):
        existing_user = CustomUser.objects.filter(email=value).first()
        if existing_user and existing_user.username != self.initial_data.get(
            'username'
        ):
            raise serializers.ValidationError("Email must be unique.")
        return value

    def validate_username(self, value):
        existing_user = CustomUser.objects.filter(username=value).first()
        if existing_user and existing_user.email != self.initial_data.get(
            'email'
        ):
            raise serializers.ValidationError("Username must be unique.")
        if not re.match(r'^[\w.@+-]+$', value) or value == 'me':
            raise serializers.ValidationError('Username is invalid.')
        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        confirmation_code = generate_confirmation_code()
        existing_user = CustomUser.objects.filter(
            email=email,
            username=username
        ).first()
        if existing_user:
            existing_user.confirmation_code = confirmation_code
            existing_user.save()
            send_confirmation_email(email, confirmation_code)
            return existing_user

        user = CustomUser.objects.create_user(
            email=email,
            username=username,
            confirmation_code=confirmation_code
        )
        send_confirmation_email(email, confirmation_code)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate(self, attrs):
        if self.context['request'].method == 'PATCH':
            username = attrs.get('username')
            if username is not None and not re.match(r'^[\w.@+-]+$', username):
                raise serializers.ValidationError(
                    r'Username must match the pattern: ^[\w.@+-]+\Z'
                )
            if 'username' not in attrs or 'email' not in attrs:
                return attrs
        return super().validate(attrs)


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


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
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
    score = serializers.IntegerField(
        min_value=MIN_SCORE_VALUE,
        max_value=MAX_SCORE_VALUE
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        user = self.context['request'].user
        title = self.context['view'].kwargs['title_id']
        if not Title.objects.filter(id=title).exists():
            return Response(
                'This title does not exist!',
                status=status.HTTP_404_NOT_FOUND
            )
        if (
            Review.objects.filter(
                author=user,
                title=title
            ).exists()
            and self.context['request'].method == 'POST'
        ):
            raise serializers.ValidationError(
                'You can leave only one review for a title!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
