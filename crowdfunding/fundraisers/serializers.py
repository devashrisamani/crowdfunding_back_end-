from pyclbr import Class
from pyexpat import model
from rest_framework import serializers
from django.apps import apps
from .models import Pledge


class PledgeSerializer(serializers.ModelSerializer):
    """
    Serializer used for listing pledges (e.g. on fundraiser detail pages).
    Handles conditional hiding of pledge comments.
    """

    # Only the API sets the supporter; expose it read-only in responses.
    supporter = serializers.ReadOnlyField(source='supporter.id')
    # This field is derived from the model and cannot be written to by users
    is_hidden_by_owner = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = apps.get_model('fundraisers.Pledge')
        fields = '__all__'

    def to_representation(self, instance):
        """
        Customise the output representation of a pledge.

        If the pledge comment is hidden by the fundraiser owner:
        - The owner can still see it
        - The supporter who made the pledge can still see it
        - Everyone else sees an empty comment
        """
        data = super().to_representation(instance)

        if instance.is_hidden_by_owner:
            request = getattr(self, 'context', {}).get('request')
            user = getattr(request, 'user', None)

            is_owner = bool(user and user.is_authenticated and user == instance.fundraiser.owner)
            is_supporter = bool(user and user.is_authenticated and user == instance.supporter)

            # Hide the comment for all other users
            if not is_owner and not is_supporter:
                data['comment'] = ''
        return data

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class PledgeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used for retrieving or updating an individual pledge.
    """

    # Read-only fields that should not be modified after creation
    id = serializers.IntegerField(read_only=True)
    amount=serializers.IntegerField(read_only=True)
    fundraiser = serializers.PrimaryKeyRelatedField(read_only=True)
    supporter = serializers.PrimaryKeyRelatedField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    is_hidden_by_owner = serializers.BooleanField(read_only=True)

    # Editable fields
    anonymous = serializers.BooleanField()
    comment = serializers.CharField()

    class Meta:
        model = Pledge
        fields = '__all__'

    def to_representation(self, instance):
        """
        Apply the same comment-hiding logic as PledgeSerializer
        when returning a single pledge.
        """
        data = super().to_representation(instance)

        if instance.is_hidden_by_owner:
            request = getattr(self, 'context', {}).get('request')
            user = getattr(request, 'user', None)

            is_owner = bool(user and user.is_authenticated and user == instance.fundraiser.owner)
            is_supporter = bool(user and user.is_authenticated and user == instance.supporter)

            if not is_owner and not is_supporter:
                data['comment'] = ''

        return data


class FundraiserSerializer(serializers.ModelSerializer):
    """
    Base serializer for fundraisers.
    Used for list views and basic data access.
    """

    # Expose the owner's ID but prevent updates via the API
    owner = serializers.ReadOnlyField(source='owner.id')
    
    class Meta:
        model = apps.get_model('fundraisers.Fundraiser')
        fields = '__all__'

    def validate_goal(self, value):
        if value <= 0:
            raise serializers.ValidationError("Goal must be greater than zero.")
        return value


class FundraiserDetailSerializer(FundraiserSerializer):
    """
    Detailed fundraiser serializer.
    Includes related pledges and supports updates.
    """
    
    # Include all related pledges (read-only)
    pledges = PledgeSerializer(many=True, read_only=True)
    
    def update(self, instance, validated_data):
        """
        Custom update method to safely update fundraiser fields.
        Only fields included in the request will be updated.
        """
        
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.goal = validated_data.get('goal', instance.goal)
        instance.image = validated_data.get('image', instance.image)
        instance.is_open = validated_data.get('is_open', instance.is_open)
        instance.date_created = validated_data.get('date_created', instance.date_created)
        instance.owner = validated_data.get('owner', instance.owner)
        
        instance.save()
        
        # Return the updated instance
        return instance
