from rest_framework import generics
from account.models import User
from account.serializers import UserSerializer




class UserListApiView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateUserApiView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer