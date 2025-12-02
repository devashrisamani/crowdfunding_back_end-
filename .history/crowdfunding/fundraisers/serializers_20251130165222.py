"""
=============================================================================
SERIALIZERS.PY - Translating Fundraiser & Pledge Data
=============================================================================

WHAT IS THIS FILE?
------------------
Serializers convert between Python objects and JSON format.
This file defines how Fundraiser and Pledge data is:
- Converted TO JSON (for API responses)
- Converted FROM JSON (for incoming requests)
- Validated before saving to the database

THREE SERIALIZERS IN THIS FILE:
-------------------------------
1. PledgeSerializer - Basic pledge data conversion
2. FundraiserSerializer - Basic fundraiser data (for lists)
3. FundraiserDetailSerializer - Detailed view (includes nested pledges)

WHY HAVE TWO FUNDRAISER SERIALIZERS?
------------------------------------
Different endpoints need different data:

List View (GET /fundraisers/):
- Shows many fundraisers
- Don't need all the pledges (too much data!)
- Use: FundraiserSerializer

Detail View (GET /fundraisers/1/):
- Shows one fundraiser
- Want to see all its pledges too
- Use: FundraiserDetailSerializer (includes nested pledges)

=============================================================================
"""

from rest_framework import serializers
from django.apps import apps
# apps.get_model() is a way to get a model without direct import
# This can help avoid circular import issues


class PledgeSerializer(serializers.ModelSerializer):
    """
    PLEDGE SERIALIZER
    =================
    
    Converts Pledge objects to/from JSON.
    
    EXAMPLE OUTPUT:
    ---------------
    {
        "id": 1,
        "amount": 100,
        "comment": "Great cause!",
        "anonymous": false,
        "fundraiser": 1,
        "supporter": 3
    }
    
    EXAMPLE INPUT (for creating):
    -----------------------------
    {
        "amount": 100,
        "comment": "Happy to help!",
        "anonymous": false,
        "fundraiser": 1,
        "supporter": 3
    }
    
    NOTE: For ForeignKey fields (fundraiser, supporter), the serializer
    uses the ID by default, not the full nested object.
    """
    
    class Meta:
        # Which model does this serializer work with?
        model = apps.get_model('fundraisers.Pledge')
        # apps.get_model('app_name.ModelName') retrieves the model class
        # This is equivalent to: from .models import Pledge; model = Pledge
        
        # Which fields to include in the serialized output?
        fields = '__all__'
        # '__all__' includes every field from the model:
        # - id (auto-created by Django)
        # - amount
        # - comment
        # - anonymous
        # - fundraiser (as ID)
        # - supporter (as ID)
        #
        # ALTERNATIVE: List specific fields
        # fields = ['id', 'amount', 'comment', 'anonymous', 'fundraiser', 'supporter']


class FundraiserSerializer(serializers.ModelSerializer):
    """
    FUNDRAISER SERIALIZER (Basic)
    =============================
    
    Used for:
    - Listing all fundraisers (GET /fundraisers/)
    - Creating a new fundraiser (POST /fundraisers/)
    
    EXAMPLE OUTPUT:
    ---------------
    {
        "id": 1,
        "owner": 5,
        "title": "Build a School",
        "description": "We're raising funds...",
        "goal": 50000,
        "image": "https://example.com/school.jpg",
        "is_open": true,
        "date_created": "2024-03-15T10:30:45Z"
    }
    
    NOTE: This serializer does NOT include pledges. That's intentional
    for performance - when listing many fundraisers, we don't want to
    load all pledges for each one.
    """
    
    owner = serializers.ReadOnlyField(source='owner.id')
    """
    READ-ONLY OWNER FIELD
    ---------------------
    
    WHAT IS ReadOnlyField?
    - A field that is ONLY included in output (serialization)
    - It cannot be set via input (deserialization)
    - Perfect for fields that should be set by the server, not the client
    
    WHY source='owner.id'?
    - By default, serializers would try to read 'owner' directly
    - source='owner.id' tells it to get the ID of the owner object
    - This gives us the number 5 instead of the full user object
    
    WHY READ-ONLY?
    - The owner should be set automatically to the logged-in user
    - We don't want users to fake ownership of fundraisers
    - The owner is set in views.py: serializer.save(owner=request.user)
    
    WITHOUT THIS LINE:
    - owner would be a writeable field
    - Someone could send: {"owner": 1, "title": "..."} 
    - They could pretend to create fundraisers as other users!
    """
    
    class Meta:
        model = apps.get_model('fundraisers.Fundraiser')
        fields = '__all__'


class FundraiserDetailSerializer(FundraiserSerializer):
    """
    FUNDRAISER DETAIL SERIALIZER (Extended)
    =======================================
    
    INHERITANCE:
    ------------
    class FundraiserDetailSerializer(FundraiserSerializer):
    
    This EXTENDS (inherits from) FundraiserSerializer, meaning:
    - It has ALL the fields from FundraiserSerializer
    - Plus the additional 'pledges' field we define here
    - Plus the custom update() method
    
    Used for:
    - Viewing a single fundraiser (GET /fundraisers/1/)
    - Updating a fundraiser (PUT /fundraisers/1/)
    
    EXAMPLE OUTPUT:
    ---------------
    {
        "id": 1,
        "owner": 5,
        "title": "Build a School",
        "description": "We're raising funds...",
        "goal": 50000,
        "image": "https://example.com/school.jpg",
        "is_open": true,
        "date_created": "2024-03-15T10:30:45Z",
        "pledges": [                              ← NEW! Nested pledges
            {
                "id": 1,
                "amount": 100,
                "comment": "Great cause!",
                "anonymous": false,
                "fundraiser": 1,
                "supporter": 3
            },
            {
                "id": 2,
                "amount": 250,
                "comment": "Happy to help!",
                "anonymous": true,
                "fundraiser": 1,
                "supporter": 7
            }
        ]
    }
    """
    
    pledges = PledgeSerializer(many=True, read_only=True)
    """
    NESTED PLEDGES
    --------------
    
    This creates a "nested" representation - the pledges are embedded
    inside the fundraiser data instead of just showing IDs.
    
    PledgeSerializer(many=True, read_only=True)
    
    PARAMETERS:
    - many=True: We're serializing a LIST of pledges (not just one)
    - read_only=True: Can't create/update pledges through this field
      (pledges are created via the /pledges/ endpoint instead)
    
    HOW DOES DJANGO KNOW WHICH PLEDGES?
    -----------------------------------
    Remember in models.py we defined:
        fundraiser = models.ForeignKey(..., related_name='pledges')
    
    This created a 'pledges' attribute on Fundraiser objects.
    The serializer field name 'pledges' matches this related_name,
    so Django automatically knows to get fundraiser.pledges.all()
    """
    
    def update(self, instance, validated_data):
        """
        CUSTOM UPDATE METHOD
        --------------------
        
        This method is called when updating an existing fundraiser.
        
        WHEN IS THIS CALLED?
        --------------------
        PUT /fundraisers/1/ with body {"title": "New Title", "goal": 60000}
        
        1. View calls serializer.is_valid()
        2. View calls serializer.save()
        3. save() calls this update() method
        
        PARAMETERS:
        -----------
        instance: The existing Fundraiser object from the database
        validated_data: Dictionary of the new values (already validated)
        
        HOW IT WORKS:
        -------------
        For each field, we use .get() with a default:
            validated_data.get('title', instance.title)
        
        This means:
        - If 'title' is in validated_data, use the new value
        - If 'title' is NOT in validated_data, keep the existing value
        
        This allows PARTIAL updates - you don't have to send all fields!
        
        RETURNS:
        --------
        The updated Fundraiser instance
        """
        # Update each field, falling back to existing value if not provided
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.goal = validated_data.get('goal', instance.goal)
        instance.image = validated_data.get('image', instance.image)
        instance.is_open = validated_data.get('is_open', instance.is_open)
        instance.date_created = validated_data.get('date_created', instance.date_created)
        instance.owner = validated_data.get('owner', instance.owner)
        
        # Save the updated instance to the database
        instance.save()
        
        # Return the updated instance
        return instance
        
        """
        ALTERNATIVE (using a loop):
        ---------------------------
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
        
        WHY NOT USE THE DEFAULT update()?
        ---------------------------------
        ModelSerializer has a default update() that does almost this.
        Defining it explicitly here lets you:
        - Add custom logic (e.g., send emails on certain changes)
        - Control exactly which fields can be updated
        - Add validation that depends on multiple fields
        """


"""
=============================================================================
SERIALIZER CHEAT SHEET
=============================================================================

COMMON FIELD TYPES:
-------------------
CharField()           - Text fields
IntegerField()        - Whole numbers
DecimalField()        - Decimal numbers
BooleanField()        - True/False
DateTimeField()       - Date and time
URLField()            - URLs
EmailField()          - Email addresses

RELATIONSHIP FIELDS:
--------------------
PrimaryKeyRelatedField()    - Shows ID (default for ForeignKey)
StringRelatedField()        - Shows __str__ representation
SlugRelatedField()          - Shows a specific field (like 'username')
Nested Serializer           - Shows full nested object

COMMON OPTIONS:
---------------
read_only=True        - Only for output, not input
write_only=True       - Only for input, not output
required=False        - Field is optional
default=value         - Default value if not provided
source='field.attr'   - Get value from a different attribute
many=True             - For lists/arrays of objects

EXAMPLE CUSTOMIZATIONS:
-----------------------
# Show owner's username instead of ID
owner = serializers.StringRelatedField()

# Only allow choosing from open fundraisers
fundraiser = serializers.PrimaryKeyRelatedField(
    queryset=Fundraiser.objects.filter(is_open=True)
)

# Custom validation
def validate_amount(self, value):
    if value <= 0:
        raise serializers.ValidationError("Amount must be positive")
    return value

=============================================================================
"""
