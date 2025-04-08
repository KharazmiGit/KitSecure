from rest_framework import generics
from account.models import User
from account.serializers import UserSerializer


# list of whole user that exist in db
class UserListApiView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# create new user in db
class CreateUserApiView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
