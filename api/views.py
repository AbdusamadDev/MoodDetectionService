from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from api.serializers import TokenSerializer


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.user.is_authenticated)
        logout(request)
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class TokenAPIView(ObtainAuthToken):
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "status": False})


class TestListAPIView(ListAPIView):
    pass
