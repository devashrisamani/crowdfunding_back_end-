"""
=============================================================================
SERIALIZERS.PY - The Translator Between Python and JSON
=============================================================================

WHAT IS THIS FILE?
------------------
Serializers convert complex data (like Python objects from the database) 
into simple formats (like JSON) that can be sent over the internet.

Think of it like a translator:
- Your database speaks "Python objects"
- Web browsers/apps speak "JSON"
- Serializers translate between them!

WHAT DOES "SERIALIZE" MEAN?
---------------------------
Serialization: Python Object → JSON (for sending data OUT)
    CustomUser object → {"id": 1, "username": "john", "email": "john@example.com"}

Deserialization: JSON → Python Object (for receiving data IN)
    {"username": "john", "password": "secret123"} → CustomUser object

WHY DO WE NEED THIS?
--------------------
1. APIs communicate using JSON, not Python objects
2. We need to control WHAT data is exposed (hide passwords!)
3. We need to VALIDATE incoming data before saving

WHEN DOES THIS RUN?
-------------------
Serializers are called from views.py:
- When someone requests user data (GET) → serialize to JSON
- When someone creates a user (POST) → deserialize from JSON, validate, save

ORDER IN THE REQUEST FLOW:
--------------------------
1. Request arrives at urls.py (routing)
2. urls.py sends it to views.py (logic)
3. views.py uses serializers.py to:
   - Convert incoming JSON to Python (deserialization)
   - Validate the data
   - Convert Python objects to JSON (serialization)
4. Response is sent back to the user

=============================================================================
"""

from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    USER SERIALIZER
    ===============
    
    This serializer handles converting CustomUser objects to/from JSON.
    
    WHAT IS ModelSerializer?
    ------------------------
    ModelSerializer is a shortcut that automatically creates serializer 
    fields based on your model. Instead of manually defining every field,
    it reads your CustomUser model and creates matching fields.
    
    Manual way (without ModelSerializer):
        username = serializers.CharField(max_length=150)
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)
        # ... and so on for every field
    
    With ModelSerializer:
        class Meta:
            model = CustomUser
            fields = '__all__'  # That's it! All fields are created automatically
    """
    
    class Meta:
        """
        THE META CLASS
        --------------
        This inner class provides "metadata" (information about the serializer).
        
        Think of it as the settings/configuration for this serializer.
        """
        
        # Which model should this serializer work with?
        model = CustomUser
        
        # Which fields should be included in the JSON?
        # '__all__' means include every field from the model
        # You could also list specific fields: ['id', 'username', 'email']
        fields = '__all__'
        
        # Extra settings for specific fields
        extra_kwargs = {
            'password': {
                'write_only': True  # SECURITY: Never send password in responses!
            }
        }
        """
        WHAT IS write_only?
        -------------------
        write_only=True means:
        - This field CAN be received (when creating/updating a user)
        - This field will NOT be sent back in responses
        
        This is crucial for passwords! You want users to be able to SET 
        their password, but you never want to EXPOSE it in API responses.
        
        Example:
        - POST request: {"username": "john", "password": "secret123"} ← password accepted
        - GET response:  {"id": 1, "username": "john"} ← password NOT included
        """

    def create(self, validated_data):
        """
        CUSTOM CREATE METHOD
        --------------------
        This method is called when a new user is being created.
        
        WHY OVERRIDE THIS?
        ------------------
        The default create() would do:
            CustomUser.objects.create(**validated_data)
        
        But this would store the password as plain text! "secret123" would
        be saved directly in the database - a massive security vulnerability!
        
        Instead, we use create_user() which:
        1. Takes the plain password "secret123"
        2. Hashes it into something like "pbkdf2_sha256$320000$..."
        3. Stores the hashed version
        
        Now even if someone steals the database, they can't read passwords!
        
        PARAMETERS:
        -----------
        validated_data: A dictionary of the data AFTER validation
            Example: {'username': 'john', 'email': 'john@test.com', 'password': 'secret123'}
        
        RETURNS:
        --------
        The newly created CustomUser object
        """
        return CustomUser.objects.create_user(**validated_data)
        # **validated_data "unpacks" the dictionary:
        # This is equivalent to:
        # CustomUser.objects.create_user(
        #     username='john',
        #     email='john@test.com', 
        #     password='secret123'
        # )
