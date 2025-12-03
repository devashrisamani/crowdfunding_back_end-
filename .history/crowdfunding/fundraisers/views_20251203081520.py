"""
=============================================================================
VIEWS.PY - The Logic Controller for Fundraisers & Pledges
=============================================================================

WHAT IS THIS FILE?
------------------
Views handle HTTP requests and return HTTP responses. They are the 
"middleman" between URLs and your data:

    URL → View → Model/Serializer → Response

Each view class handles one "resource" and defines what happens for
different HTTP methods (GET, POST, PUT, DELETE).

VIEWS IN THIS FILE:
-------------------
1. FundraiserList    - GET /fundraisers/ (list all) + POST (create new)
2. FundraiserDetail  - GET /fundraisers/<id>/ (single) + PUT (update)
3. PledgeList        - GET /pledges/ (list all) + POST (create new)

REST API CONVENTIONS:
---------------------
HTTP Method | URL Pattern        | Action
------------|-------------------|--------
GET         | /fundraisers/     | List all fundraisers
POST        | /fundraisers/     | Create a new fundraiser
GET         | /fundraisers/1/   | Get fundraiser with id=1
PUT         | /fundraisers/1/   | Update fundraiser with id=1
DELETE      | /fundraisers/1/   | Delete fundraiser with id=1 (not implemented)

=============================================================================
"""

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .models import Fundraiser, Pledge
from .serializers import FundraiserSerializer, PledgeSerializer, FundraiserDetailSerializer
from .permissions import IsOwnerOrReadOnly


class FundraiserList(APIView):
    """
    FUNDRAISER LIST VIEW
    ====================
    
    Endpoint: /fundraisers/
    Methods: GET (list all), POST (create new)
    
    PERMISSIONS:
    ------------
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    This means:
    - Anyone can READ (GET request) - no login needed
    - Only logged-in users can WRITE (POST request)
    
    This makes sense for a crowdfunding site:
    - Visitors can browse fundraisers
    - Only registered users can create fundraisers
    """
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    """
    WHAT ARE PERMISSION CLASSES?
    ----------------------------
    Permissions control WHO can access your views.
    
    Common permission classes:
    - AllowAny: Everyone can access
    - IsAuthenticated: Only logged-in users
    - IsAuthenticatedOrReadOnly: Logged in to write, anyone can read
    - IsAdminUser: Only admin/staff users
    - Custom permissions: Like our IsOwnerOrReadOnly
    
    HOW AUTHENTICATION WORKS:
    -------------------------
    1. User logs in at /api-token-auth/
    2. They receive a token: "abc123xyz..."
    3. They include it in requests: Authorization: Token abc123xyz...
    4. Django REST Framework checks the token
    5. request.user is set to the authenticated user
    """

    def get(self, request):
        """
        GET METHOD - List All Fundraisers
        ----------------------------------
        
        Called when: GET /fundraisers/
        Permission: Anyone (public)
        
        FLOW:
        -----
        1. Query database for all fundraisers
        2. Serialize them (convert to JSON format)
        3. Return the JSON list
        
        EXAMPLE RESPONSE:
        -----------------
        [
            {
                "id": 1,
                "title": "Build a School",
                "owner": 5,
                ...
            },
            {
                "id": 2,
                "title": "Save the Rainforest",
                "owner": 3,
                ...
            }
        ]
        """
        # Get all fundraisers from the database
        fundraisers = Fundraiser.objects.all()
        # This returns a QuerySet - a lazy database query
        # You can add filters: Fundraiser.objects.filter(is_open=True)
        
        # Serialize the fundraisers (convert to JSON-ready dictionaries)
        serializer = FundraiserSerializer(fundraisers, many=True)
        # many=True because we're serializing multiple objects
        
        # Return the response (status 200 OK is the default)
        return Response(serializer.data)
    
    def post(self, request):
        """
        POST METHOD - Create a New Fundraiser
        --------------------------------------
        
        Called when: POST /fundraisers/ with fundraiser data
        Permission: Authenticated users only
        
        FLOW:
        -----
        1. Create serializer with incoming data
        2. Validate the data
        3. If valid: Save (with owner = current user) and return 201
        4. If invalid: Return errors with 400
        
        EXAMPLE REQUEST:
        ----------------
        POST /fundraisers/
        Headers: Authorization: Token abc123...
        Body: {
            "title": "Build a School",
            "description": "We need your help...",
            "goal": 50000,
            "image": "https://example.com/image.jpg",
            "is_open": true
        }
        
        Note: Owner is NOT in the request - it's set automatically!
        """
        # Create serializer with the incoming JSON data
        serializer = FundraiserSerializer(data=request.data)
        # request.data contains the parsed JSON body
        
        # Validate the data
        if serializer.is_valid():
            # is_valid() checks:
            # - Required fields are present
            # - Field types are correct
            # - Custom validation passes
            
            # Save with owner set to the current user
            serializer.save(owner=request.user)
            # IMPORTANT: owner=request.user sets the fundraiser's owner
            # This is why 'owner' is ReadOnlyField in the serializer
            # The logged-in user automatically becomes the owner
            
            # Return the created fundraiser with 201 Created status
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
            # HTTP 201 = Created: The request succeeded and a new resource was created
        
        # If validation failed, return errors with 400 Bad Request
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        # serializer.errors might look like:
        # {"title": ["This field is required."]}
        # {"goal": ["A valid integer is required."]}


class FundraiserDetail(APIView):
    """
    FUNDRAISER DETAIL VIEW
    ======================
    
    Endpoint: /fundraisers/<int:pk>/
    Methods: GET (view details), PUT (update)
    
    PERMISSIONS:
    ------------
    Two permission classes work together:
    1. IsAuthenticatedOrReadOnly - Login to write, anyone can read
    2. IsOwnerOrReadOnly - Only the owner can modify their fundraiser
    
    Combined effect:
    - Anyone can VIEW any fundraiser
    - Only the OWNER can UPDATE their fundraiser
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly  # Custom permission from permissions.py
    ]
    """
    MULTIPLE PERMISSION CLASSES
    ---------------------------
    When you have multiple permission classes, ALL must pass.
    
    Example: PUT /fundraisers/1/ by User #3
    
    Check 1 (IsAuthenticatedOrReadOnly):
    - Is user logged in? YES → Pass ✓
    
    Check 2 (IsOwnerOrReadOnly):
    - Is this a safe method? NO (PUT modifies data)
    - Is user the owner of fundraiser #1? 
      - If YES → Pass ✓
      - If NO → Denied ✗
    """

    def get_object(self, pk):
        """
        HELPER METHOD - Get a Single Fundraiser
        ----------------------------------------
        
        This helper method:
        1. Tries to find a fundraiser with the given ID
        2. Checks permissions (IsOwnerOrReadOnly)
        3. Returns the object or raises 404
        
        WHY check_object_permissions?
        -----------------------------
        Object-level permissions need the actual object to check.
        For example, IsOwnerOrReadOnly needs to check:
            obj.owner == request.user
        
        So we must call check_object_permissions AFTER we have the object.
        """
        try:
            # Try to find the fundraiser
            fundraiser = Fundraiser.objects.get(pk=pk)
            
            # Check object-level permissions
            self.check_object_permissions(self.request, fundraiser)
            # This calls IsOwnerOrReadOnly.has_object_permission()
            # If the check fails, it raises PermissionDenied
            
            return fundraiser
            
        except Fundraiser.DoesNotExist:
            # Fundraiser with this ID doesn't exist
            raise Http404
            # Returns: {"detail": "Not found."}
      
    def get(self, request, pk):
        """
        GET METHOD - View Fundraiser Details
        -------------------------------------
        
        Called when: GET /fundraisers/1/
        Permission: Anyone (public)
        
        Uses FundraiserDetailSerializer which includes nested pledges.
        
        EXAMPLE RESPONSE:
        -----------------
        {
            "id": 1,
            "title": "Build a School",
            "description": "...",
            "goal": 50000,
            "image": "...",
            "is_open": true,
            "date_created": "2024-03-15T10:30:45Z",
            "owner": 5,
            "pledges": [
                {"id": 1, "amount": 100, ...},
                {"id": 2, "amount": 250, ...}
            ]
        }
        """
        # Get the fundraiser (or 404)
        fundraiser = self.get_object(pk)
        
        # Serialize with the DETAIL serializer (includes pledges)
        serializer = FundraiserDetailSerializer(fundraiser)
        # Note: no many=True because it's a single object
        
        return Response(serializer.data)


    def put(self, request, pk):
        """
        PUT METHOD - Update a Fundraiser
        ---------------------------------
        
        Called when: PUT /fundraisers/1/ with updated data
        Permission: Owner only (IsOwnerOrReadOnly)
        
        FLOW:
        -----
        1. Get the existing fundraiser
        2. Create serializer with existing instance + new data
        3. Validate and save
        4. Return updated data or errors
        
        EXAMPLE REQUEST:
        ----------------
        PUT /fundraisers/1/
        Headers: Authorization: Token abc123...
        Body: {"title": "Updated Title", "goal": 75000}
        
        PARTIAL UPDATES:
        ----------------
        partial=True allows sending only the fields you want to update.
        Without it, you'd have to send ALL fields every time.
        """
        # Get the existing fundraiser (permission check happens here)
        fundraiser = self.get_object(pk)
        
        # Create serializer with:
        # - instance: the existing fundraiser
        # - data: the new data from the request
        # - partial: allow partial updates
        serializer = FundraiserDetailSerializer(
            instance=fundraiser,
            data=request.data,
            partial=True
        )
        
        # Validate and save
        if serializer.is_valid():
            serializer.save()
            # This calls the update() method in FundraiserDetailSerializer
            return Response(serializer.data)
        
        # Return errors if validation failed
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
  
#   DELETE METHOD - Delete a Fundraiser
    def delete(self,request,pk):
        """
        DELETE METHOD - Delete a Fundraiser
        ------------------------------------
        
        Called when: DELETE /fundraisers/1/
        Permission: Owner only (IsOwnerOrReadOnly)
        
        FLOW:
        -----
        1. Get the fundraiser (permission check happens here)
        2. Delete the fundraiser
        3. Return 204 No Content
        
        EXAMPLE REQUEST:
        ----------------
        DELETE /fundraisers/1/
        Headers: Authorization: Token abc123...
        """
        fundraiser = self.get_object(pk)
        fundraiser.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  

class PledgeList(APIView):
    """
    PLEDGE LIST VIEW
    ================
    
    Endpoint: /pledges/
    Methods: GET (list all), POST (create new)
    
    NOTE: No permission classes defined here!
    This means the default applies (from settings.py or AllowAny).
    
    In a real app, you might want:
    - permission_classes = [permissions.IsAuthenticatedOrReadOnly]
      (require login to create pledges)
    
    You might also want to auto-set supporter like we do with owner:
    - serializer.save(supporter=request.user)
    """
    
    def get(self, request):
        """
        GET METHOD - List All Pledges
        ------------------------------
        
        Returns all pledges in the system.
        
        NOTE: In a real app, you might want to filter this:
        - Only pledges for a specific fundraiser
        - Only pledges by the current user
        - Only non-anonymous pledges
        
        EXAMPLE:
        --------
        # Filter by fundraiser
        fundraiser_id = request.query_params.get('fundraiser')
        if fundraiser_id:
            pledges = Pledge.objects.filter(fundraiser_id=fundraiser_id)
        """
        pledges = Pledge.objects.all()
        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        POST METHOD - Create a New Pledge
        ----------------------------------
        
        Creates a pledge to a fundraiser.
        
        EXAMPLE REQUEST:
        ----------------
        POST /pledges/
        Body: {
            "amount": 100,
            "comment": "Happy to help!",
            "anonymous": false,
            "fundraiser": 1,
            "supporter": 3
        }
        
        NOTE ON IMPROVEMENTS:
        ---------------------
        Currently, supporter must be sent in the request body.
        Better approach would be:
        
        1. Require authentication
        2. Auto-set supporter to logged-in user:
           serializer.save(supporter=request.user)
        3. Make supporter read-only in the serializer
        
        This prevents users from creating pledges as other users!
        """
        serializer = PledgeSerializer(data=request.data)
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

# Define a class for pledge detail view
class PledgeDetail(APIView):
    permission_classes = {

    }

    def get_object(self, pk):

    # Get an details of an individual pledge
    def get(self, request, pk):

    # Edit details of a comment/ anonymous status of an individual pledge
    def put(self,request, pk):


    serializer = PledgeSerializer(
        instance=pledge,
        data=request.data,
        partial=True  # ← This is key!
    )

    # After serializer.is_valid():
    serializer.save()  # This won't change supporter because it's read_only



# Add Get, Put, Delete functions 
# What happens when you delete and update the pledge? 
# Pledge permissions 

"""
=============================================================================
HTTP STATUS CODES CHEAT SHEET
=============================================================================

SUCCESS (2xx):
--------------
200 OK             - Request succeeded (default for Response())
201 Created        - Resource was created (POST success)
204 No Content     - Success, but nothing to return (DELETE success)

CLIENT ERRORS (4xx):
--------------------
400 Bad Request    - Invalid data sent by client
401 Unauthorized   - Authentication required
403 Forbidden      - Authenticated but not allowed
404 Not Found      - Resource doesn't exist
405 Method Not Allowed - HTTP method not supported

SERVER ERRORS (5xx):
--------------------
500 Internal Server Error - Something broke on the server

USING STATUS CODES:
-------------------
from rest_framework import status

return Response(data, status=status.HTTP_201_CREATED)
return Response(errors, status=status.HTTP_400_BAD_REQUEST)

=============================================================================
VIEW PATTERNS CHEAT SHEET
=============================================================================

COMMON PATTERNS FOR VIEWS:
--------------------------

# List + Create (collection endpoint)
class ItemList(APIView):
    def get(self, request):     # List all
    def post(self, request):    # Create new

# Retrieve + Update + Delete (item endpoint)
class ItemDetail(APIView):
    def get(self, request, pk):     # Get one
    def put(self, request, pk):     # Update
    def delete(self, request, pk):  # Delete

# Common helper method
def get_object(self, pk):
    try:
        return Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        raise Http404

=============================================================================
"""
