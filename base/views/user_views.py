from django.shortcuts import render

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
# from .products import products
from  django.contrib.auth.models import User

from base.serializer import ProductSerializer,UserSerializer,UserSerializerWithToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
#this import is for hashing the password
from django.contrib.auth.hashers import make_password
#thsi import will help us identify whether the user trying to register is not register in our database
from rest_framework import status

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)

    #     # Add custom claims
    #     token['username'] = user.username
    #     token['message'] = 'Hello User'
    #     # ...
    #     return token
    #we overriding the validate method and we are sterilizing more information about our users
    def validate(self, attrs):
        data = super().validate(attrs)

        # data['username'] = self.user.username
        # data['email'] = self.user.email
        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v

        return data
#in here we have our view and takes in our ObtainPairView
class MyTokenObtainPairView(TokenObtainPairView):
    #all we are doning changing the serializer class that contains our data
    serializer_class = MyTokenObtainPairSerializer

@api_view(['PUT'])#Because we are request data we use PUT request
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    #many is set to false because it's not going to return a single user 
    serializer = UserSerializerWithToken(user,many=False)
    data = request.data
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    if data['password'] != '':
        user.password = make_password(data['password'])    
    user.save() 
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    #many is set to false because it's not going to return a single user 
    serializer = UserSerializer(user,many=False)
    return Response(serializer.data)

    
#this function is for super user
@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users=User.objects.all()
    serializer = UserSerializer(users,many=True)
    return Response(serializer.data)

@api_view(['POST'])
def registerUser(request):
    try:
        data = request.data
        user = User.objects.create(
            first_name = data['name'],
            username = data['email'],
            email = data['email'],
            #for the passwor we have to hash it using the function
            password = make_password(data['password'])
        )
        serializer = UserSerializerWithToken(user,many=False)#many is set false because we returning one user
        #the after serialized is going to be returned to the frontend
        return Response(serializer.data)
    except:
         message = {'detail':'User with this email already exits'}
         return Response(message,status=status.HTTP_400_BAD_REQUEST)

# this view is to edit the from the admin panel

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request,pk):
    user=User.objects.get(id=pk)
    serializer = UserSerializer(user,many=False)
    return Response(serializer.data)

@api_view(['PUT'])#Because we are request data we use PUT request
@permission_classes([IsAdminUser])
def updateUser(request,pk):
    user = User.objects.get(id=pk)
    #many is set to false because it's not going to return a single user 
    data = request.data
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    user.is_staff = data['isAdmin']

    user.save()
    serializer = UserSerializer(user,many=False) 
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request,pk):
    userForDeletion = User.objects.get(id=pk)
    userForDeletion.delete()
    return Response('User was deleted')


