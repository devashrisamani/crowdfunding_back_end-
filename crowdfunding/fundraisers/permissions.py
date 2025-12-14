from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission that allows full access to the object owner,
    but read-only access to all other users.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if the request is safe (read-only),
        or if the requesting user is the object owner.
        """    
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only granted to the owner
        return obj.owner == request.user
        

class IsSupporterOrReadOnly(permissions.BasePermission):
    """
    Object-level permission that allows full access to the pledge supporter,
    but read-only access to all other users.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Return True if the request is safe (read-only),
        or if the requesting user is the pledge supporter.
        """

        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only granted to the supporter   
        return obj.supporter == request.user
        

# Add pledge to add to the fundraiser only if it is open - Permission


class IsSupporterOrFundraiserOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission that allows write access to:
    - the user who made the pledge (supporter), OR
    - the owner of the associated fundraiser.

    All other users have read-only access.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if the request is safe (read-only),
        or if the user is either the pledge supporter or fundraiser owner.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.supporter == request.user or obj.fundraiser.owner == request.user
