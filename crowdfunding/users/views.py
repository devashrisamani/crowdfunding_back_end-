from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import CustomUser
from .serializers import CustomUserSerializer


class CustomUserList(APIView): 
     
    def get(self, request):
       
        #Get all users from the database
        users = CustomUser.objects.all()

        serializer = CustomUserSerializer(users, many=True)
        # many=True is required because we're serializing a LIST of users
        # Without it, the serializer expects a single object
        
        return Response(serializer.data)
        # serializer.data contains the JSON-ready dictionary/list

    def post(self, request):
       
        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
       

class CustomUserDetail(APIView):
    
    def get_object(self, pk):

        try:
            # Try to find a user with this ID
            return CustomUser.objects.get(pk=pk)
            # .get() returns exactly ONE object
        except CustomUser.DoesNotExist:
            # If user doesn't exist, raise a 404 error
            raise Http404

    def get(self, request, pk):

        user = self.get_object(pk)
        
        serializer = CustomUserSerializer(user)
        
        return Response(serializer.data)


class CustomAuthToken(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        
        #Use the built-in serializer to validate credentials
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        # Validate 
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data["user"]
        
        token, created = Token.objects.get_or_create(user=user)
        
        
        # Step 5: Return the token and user info
        return Response({
            'token': token.key,      # The actual token string
            'user_id': user.id,      # User's database ID
            'email': user.email      # User's email
        })
     
