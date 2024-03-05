import string, secrets

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings

from reviews.models import CustomUser 


def generate_confirmation_code(length=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_confirmation_email(email, confirmation_code):
    send_mail(subject='Confirmation Code', 
              message=f'Your confirmation code is: {confirmation_code}', 
              from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[email])


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=True)
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

