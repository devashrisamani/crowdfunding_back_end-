from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission that allows full access to the object owner,
    but read-only access to all other users.
    """
    
    def has_object_permission(self, request, view, obj):
        
        #Check if this is a "safe" (read-only) method
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # check if the current user is the owner
        return obj.owner == request.user
        # This returns True if the user owns this object
        # Returns False if they don't (triggering a 403 Forbidden)
        


class IsSupporterOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.supporter == request.user
        

# Add pledge to add to the fundraiser only if it is open - Permission


class IsSupporterOrFundraiserOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows pledge edits for the pledge supporter OR the fundraiser owner.
    Read-only access for everyone else.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.supporter == request.user or obj.fundraiser.owner == request.user
