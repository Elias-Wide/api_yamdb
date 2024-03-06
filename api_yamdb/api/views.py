from rest_framework import status, views, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import CustomUser
from api.serializers import (
    SignUpSerializer, GetTokenSerializer, UserProfileSerializer
)


class SignUpView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)


class TokenView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            confirmation_code = serializer.validated_data.get('confirmation_code')
            user = CustomUser.objects.filter(
                username=username, confirmation_code=confirmation_code).first()
            if user:
                refresh = RefreshToken.for_user(user)
                user.confirmation_code = None
                user.save()
                return Response(
                    {'refresh': str(refresh), 'access': str(refresh.access_token)}, 
                    status=status.HTTP_200_OK)
            return Response(
                {'error': 'Invalid username or verification code'}, 
                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get(self, request, format=None):
        serializer = UserProfileSerializer(self.get_object())
        return Response(serializer.data)

    def patch(self, request, format=None):
        instance = self.get_object()
        serializer = UserProfileSerializer(
            instance, 
            data=request.data, 
            partial=True, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
