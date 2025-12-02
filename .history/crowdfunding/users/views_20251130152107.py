"""
=============================================================================
VIEWS.PY - The Brain of Your Application
=============================================================================

WHAT IS THIS FILE?
------------------
Views contain the LOGIC of your application. When a request comes in,
views decide:
1. What data to fetch from the database
2. What processing to do
3. What response to send back

Think of views as "request handlers" - they receive requests and return responses.

ANALOGY:
--------
If your app was a restaurant:
- urls.py is the HOST (directs customers to the right table)
- views.py is the WAITER (takes orders, brings food)
- models.py is the MENU (defines what's available)
- serializers.py is the KITCHEN (prepares the food)

TYPES OF VIEWS IN DJANGO:
-------------------------
1. Function-based views (FBV) - Simple functions
2. Class-based views (CBV) - Classes with methods for GET, POST, etc.

This file uses Class-based views with Django REST Framework's APIView.

ORDER IN THE REQUEST FLOW:
--------------------------
1. User sends HTTP request (e.g., GET /users/)
2. urls.py matches the URL pattern and calls the appropriate view
3. View's get() or post() method runs
4. View uses serializers to process data
5. View returns a Response object
6. Django converts Response to HTTP and sends to user

=============================================================================
"""

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
    """
    USER LIST VIEW
    ==============
    
    Handles requests to: /users/
    
    This view handles:
    - GET /users/ → List all users
    - POST /users/ → Create a new user (registration)
    
    WHAT IS APIView?
    ----------------
    APIView is Django REST Framework's base class for views. It provides:
    - Request parsing (automatically reads JSON from requests)
    - Response rendering (automatically converts to JSON)
    - Authentication/permission checking
    - Exception handling
    
    HOW IT WORKS:
    -------------
    When a request comes in, APIView looks at the HTTP method and calls
    the corresponding method:
    - GET request → calls get() method
    - POST request → calls post() method
    - PUT request → calls put() method
    - DELETE request → calls delete() method
    """
  
    def get(self, request):
        """
        GET METHOD - List All Users
        ----------------------------
        
        Called when: Someone visits GET /users/
        Purpose: Return a list of all users in the system
        
        STEP BY STEP:
        1. Query the database for all CustomUser objects
        2. Pass them to the serializer (converts to JSON-ready format)
        3. Return the serialized data as a Response
        
        PARAMETERS:
        -----------
        request: The HTTP request object containing:
            - request.method ('GET')
            - request.user (who's making the request)
            - request.data (any data sent - empty for GET)
        
        RETURNS:
        --------
        Response object containing a list of all users as JSON
        Example: [
            {"id": 1, "username": "alice", "email": "alice@test.com"},
            {"id": 2, "username": "bob", "email": "bob@test.com"}
        ]
        """
        # Step 1: Get all users from the database
        users = CustomUser.objects.all()
        # This creates a QuerySet - a lazy database query
        # "Lazy" means it doesn't hit the database until you actually use the data
        
        # Step 2: Serialize the users (convert Python objects → JSON-ready data)
        serializer = CustomUserSerializer(users, many=True)
        # many=True is required because we're serializing a LIST of users
        # Without it, the serializer expects a single object
        
        # Step 3: Return the response
        return Response(serializer.data)
        # serializer.data contains the JSON-ready dictionary/list
        # Response() wraps it in a proper HTTP response

    def post(self, request):
        """
        POST METHOD - Create a New User (Registration)
        -----------------------------------------------
        
        Called when: Someone sends POST /users/ with user data
        Purpose: Create a new user account
        
        STEP BY STEP:
        1. Take the incoming JSON data from the request
        2. Pass it to the serializer for validation
        3. If valid, save to database and return success
        4. If invalid, return error messages
        
        PARAMETERS:
        -----------
        request: The HTTP request object containing:
            - request.data: The JSON data sent by the client
              Example: {"username": "newuser", "password": "secret123", "email": "new@test.com"}
        
        RETURNS:
        --------
        Success (201 Created): The created user data
        Failure (400 Bad Request): Validation error messages
        """
        # Step 1: Create a serializer with the incoming data
        serializer = CustomUserSerializer(data=request.data)
        # request.data contains the JSON sent by the client
        # The serializer will validate this data against our model's rules
        
        # Step 2: Check if the data is valid
        if serializer.is_valid():
            # is_valid() checks things like:
            # - Are required fields present?
            # - Are field types correct (string, number, etc.)?
            # - Does username already exist?
            # - Is email format valid?
            
            # Step 3a: Data is valid - save to database
            serializer.save()
            # This calls our custom create() method in the serializer
            # which properly hashes the password
            
            # Return the created user data with 201 Created status
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
            # HTTP 201 means "Created" - the resource was successfully created
        
        # Step 3b: Data is invalid - return errors
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
        # serializer.errors contains messages like:
        # {"username": ["This field is required."]}
        # {"email": ["Enter a valid email address."]}
        # HTTP 400 means "Bad Request" - the client sent invalid data


class CustomUserDetail(APIView):
    """
    USER DETAIL VIEW
    ================
    
    Handles requests to: /users/<id>/
    
    This view handles:
    - GET /users/1/ → Get details of user with id=1
    
    The <int:pk> in the URL captures the user's ID (primary key).
    """
    
    def get_object(self, pk):
        """
        HELPER METHOD - Get a Single User
        ----------------------------------
        
        This is a helper method (not an HTTP handler) that retrieves
        a user by their primary key (ID).
        
        WHY HAVE THIS HELPER?
        ---------------------
        Multiple HTTP methods (get, put, delete) need to find a user by ID.
        Instead of duplicating the code, we put it in this helper method.
        
        PARAMETERS:
        -----------
        pk (primary key): The user's ID number
        
        RETURNS:
        --------
        CustomUser object if found
        
        RAISES:
        -------
        Http404 if user doesn't exist (returns "Not Found" page)
        """
        try:
            # Try to find a user with this ID
            return CustomUser.objects.get(pk=pk)
            # .get() returns exactly ONE object
            # If no match found, raises DoesNotExist
            # If multiple matches found, raises MultipleObjectsReturned
        except CustomUser.DoesNotExist:
            # If user doesn't exist, raise a 404 error
            raise Http404
            # This automatically returns a "404 Not Found" response

    def get(self, request, pk):
        """
        GET METHOD - Get Single User Details
        ------------------------------------
        
        Called when: Someone visits GET /users/1/
        Purpose: Return details of a specific user
        
        PARAMETERS:
        -----------
        request: The HTTP request object
        pk: The user's ID from the URL (e.g., 1 from /users/1/)
        
        RETURNS:
        --------
        User data as JSON
        Example: {"id": 1, "username": "alice", "email": "alice@test.com"}
        """
        # Step 1: Find the user (or return 404)
        user = self.get_object(pk)
        
        # Step 2: Serialize the user (no many=True - single object)
        serializer = CustomUserSerializer(user)
        
        # Step 3: Return the response
        return Response(serializer.data)


class CustomAuthToken(ObtainAuthToken):
    """
    CUSTOM AUTHENTICATION TOKEN VIEW
    =================================
    
    Handles: POST /api-token-auth/
    
    This view handles user LOGIN. When a user provides correct credentials,
    they receive a TOKEN that they can use for future authenticated requests.
    
    WHAT IS TOKEN AUTHENTICATION?
    -----------------------------
    Instead of sending username/password with every request (insecure!),
    the user logs in ONCE and gets a token (a long random string).
    
    They include this token in the header of future requests:
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    
    WHAT IS ObtainAuthToken?
    ------------------------
    A built-in Django REST Framework view that handles the login process.
    We're extending it to customize what data we return after login.
    
    FLOW:
    -----
    1. User sends: POST /api-token-auth/ with {"username": "x", "password": "y"}
    2. Django validates credentials
    3. If valid, we return a token (and some user info)
    4. User stores this token and uses it for authenticated requests
    """
    
    def post(self, request, *args, **kwargs):
        """
        POST METHOD - Login and Get Token
        ----------------------------------
        
        Called when: User sends POST /api-token-auth/ with credentials
        Purpose: Validate login and return authentication token
        
        PARAMETERS:
        -----------
        request.data should contain:
            {"username": "alice", "password": "secret123"}
        
        RETURNS:
        --------
        Success: {"token": "abc123...", "user_id": 1, "email": "alice@test.com"}
        Failure: {"non_field_errors": ["Unable to log in with provided credentials."]}
        """
        # Step 1: Use the built-in serializer to validate credentials
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        # self.serializer_class is ObtainAuthToken's built-in serializer
        # It checks if username/password are correct
        
        # Step 2: Validate (this will raise an exception if invalid)
        serializer.is_valid(raise_exception=True)
        # raise_exception=True means if validation fails, it automatically
        # returns a 400 error response - we don't need to handle it manually
        
        # Step 3: Get the validated user
        user = serializer.validated_data["user"]
        # If we get here, the login was successful
        # validated_data contains the authenticated user object
        
        # Step 4: Get or create a token for this user
        token, created = Token.objects.get_or_create(user=user)
        # get_or_create returns a tuple: (object, was_created_bool)
        # - If user already has a token, return it (created=False)
        # - If not, create a new one (created=True)
        
        # Step 5: Return the token and user info
        return Response({
            'token': token.key,      # The actual token string
            'user_id': user.id,      # User's database ID
            'email': user.email      # User's email
        })
        # The client stores this token and includes it in future requests:
        # Authorization: Token <token.key>
