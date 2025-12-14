from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        
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
        


class IsSupporterOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.supporter == request.user
        

# Add pledge to add to the fundraiser only if it is open - Permission