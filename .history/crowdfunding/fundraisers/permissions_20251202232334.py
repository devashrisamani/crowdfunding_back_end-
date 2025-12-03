"""
=============================================================================
PERMISSIONS.PY - Custom Permission Classes
=============================================================================

WHAT IS THIS FILE?
------------------
This file defines CUSTOM permission classes that control who can do what.

Django REST Framework comes with built-in permissions:
- AllowAny: Everyone can access
- IsAuthenticated: Only logged-in users
- IsAuthenticatedOrReadOnly: Login to write, anyone can read
- IsAdminUser: Only admin/staff users

But sometimes you need custom logic, like:
- "Only the owner of this object can modify it"
- "Users can only see their own data"
- "Premium users get extra access"

That's what this file is for!

HOW PERMISSIONS WORK:
---------------------
1. View has permission_classes = [SomePermission]
2. Before the view runs, Django calls the permission's methods
3. Permission returns True (allowed) or False (denied)
4. If denied, user gets a 403 Forbidden response

TWO TYPES OF PERMISSION CHECKS:
-------------------------------
1. View-level: has_permission(request, view)
   - Called for ALL requests to this view
   - Doesn't have access to the specific object yet
   - Example: "Is the user logged in?"

2. Object-level: has_object_permission(request, view, obj)
   - Called when accessing a SPECIFIC object
   - Can check properties of the object
   - Example: "Is this user the owner of this fundraiser?"

=============================================================================
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    CUSTOM PERMISSION: IS OWNER OR READ ONLY
    =========================================
    
    This permission class allows:
    - ANYONE to perform safe/read-only operations (GET, HEAD, OPTIONS)
    - ONLY THE OWNER to perform unsafe/write operations (POST, PUT, DELETE)
    
    USE CASE:
    ---------
    You want visitors to view fundraisers, but only the creator
    should be able to edit or delete their own fundraiser.
    
    EXAMPLE:
    --------
    Fundraiser #1 owned by User #5 (Alice)
    
    - GET /fundraisers/1/ by anyone → Allowed ✓
    - PUT /fundraisers/1/ by Alice (User #5) → Allowed ✓
    - PUT /fundraisers/1/ by Bob (User #3) → Denied ✗
    
    WHERE IS THIS USED?
    -------------------
    In views.py:
        class FundraiserDetail(APIView):
            permission_classes = [
                permissions.IsAuthenticatedOrReadOnly,
                IsOwnerOrReadOnly  ← This class!
            ]
    """
    
    def has_object_permission(self, request, view, obj):
        """
        CHECK IF THE USER HAS PERMISSION TO ACCESS THIS OBJECT
        -------------------------------------------------------
        
        This method is called by view.check_object_permissions()
        after the object has been retrieved from the database.
        
        PARAMETERS:
        -----------
        request: The HTTP request object
            - request.method: 'GET', 'POST', 'PUT', 'DELETE', etc.
            - request.user: The authenticated user (or AnonymousUser)
        
        view: The view class handling this request
            - Useful if you need view-specific logic
        
        obj: The object being accessed
            - In our case, a Fundraiser object
            - Has an 'owner' attribute we can check
        
        RETURNS:
        --------
        True: Permission granted (proceed with the request)
        False: Permission denied (return 403 Forbidden)
        """
        
        # STEP 1: Check if this is a "safe" (read-only) method
        if request.method in permissions.SAFE_METHODS:
            # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
            # These methods don't modify data, so anyone can use them
            return True
        
        # STEP 2: For unsafe methods (POST, PUT, PATCH, DELETE),
        # check if the current user is the owner
        return obj.owner == request.user
        # This returns True if the user owns this object
        # Returns False if they don't (triggering a 403 Forbidden)
        

        
        """
        BREAKDOWN:
        ----------
        
        obj.owner → The user who created this fundraiser (a CustomUser object)
        request.user → The user making this request (a CustomUser object or AnonymousUser)
        
        obj.owner == request.user compares them:
        - If same user → True → Permission granted
        - If different users → False → Permission denied
        
        Note: If the user is not logged in, request.user is AnonymousUser,
        which will never equal obj.owner.
        """


"""
=============================================================================
HOW PERMISSION CLASSES ARE USED TOGETHER
=============================================================================

In FundraiserDetail view:
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]

When a request comes in, BOTH permissions are checked.
The request is only allowed if ALL permissions return True.

EXAMPLE SCENARIOS:
------------------

Scenario 1: Anonymous user does GET /fundraisers/1/
    IsAuthenticatedOrReadOnly:
        - Is it a safe method? YES (GET)
        - Result: ✓ Allowed
    IsOwnerOrReadOnly:
        - Is it a safe method? YES (GET)
        - Result: ✓ Allowed
    FINAL: ✓ Request proceeds

Scenario 2: Anonymous user does PUT /fundraisers/1/
    IsAuthenticatedOrReadOnly:
        - Is it a safe method? NO (PUT)
        - Is user authenticated? NO
        - Result: ✗ Denied
    FINAL: ✗ 403 Forbidden (doesn't even check IsOwnerOrReadOnly)

Scenario 3: Alice (owner) does PUT /fundraisers/1/
    IsAuthenticatedOrReadOnly:
        - Is it a safe method? NO (PUT)
        - Is user authenticated? YES
        - Result: ✓ Allowed
    IsOwnerOrReadOnly:
        - Is it a safe method? NO (PUT)
        - Is user the owner? YES (Alice created this fundraiser)
        - Result: ✓ Allowed
    FINAL: ✓ Request proceeds

Scenario 4: Bob (not owner) does PUT /fundraisers/1/
    IsAuthenticatedOrReadOnly:
        - Is it a safe method? NO (PUT)
        - Is user authenticated? YES
        - Result: ✓ Allowed
    IsOwnerOrReadOnly:
        - Is it a safe method? NO (PUT)
        - Is user the owner? NO (Alice owns it, not Bob)
        - Result: ✗ Denied
    FINAL: ✗ 403 Forbidden

=============================================================================
CREATING MORE CUSTOM PERMISSIONS
=============================================================================

# Only superusers can delete
class IsSuperuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

# Users can only access their own data
class IsOwnUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user  # The object IS the user

# Only allow if fundraiser is still open
class FundraiserIsOpen(permissions.BasePermission):
    message = "This fundraiser is no longer accepting pledges."
    
    def has_object_permission(self, request, view, obj):
        return obj.fundraiser.is_open

=============================================================================
"""
