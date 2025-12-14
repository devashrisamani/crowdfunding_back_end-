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

    # This field is derived from the model and cannot be written to by users
    is_hidden_by_owner = serializers.BooleanField(read_only=True)
    
    class Meta:
        # Which model does this serializer work with?
        model = apps.get_model('fundraisers.Pledge')
        fields = '__all__'

    def to_representation(self, instance):
        """
        Hide the comment text from public viewers when the owner has hidden it.
        Owners and the pledge supporter still see the original comment.
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


class PledgeDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    amount=serializers.IntegerField(read_only=True)
    fundraiser = serializers.PrimaryKeyRelatedField(read_only=True)
    supporter = serializers.PrimaryKeyRelatedField(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)
    is_hidden_by_owner = serializers.BooleanField(read_only=True)

    anonymous = serializers.BooleanField()
    comment = serializers.CharField()

    class Meta:
        model = Pledge
        fields = '__all__'

    def to_representation(self, instance):
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
    
    owner = serializers.ReadOnlyField(source='owner.id')
    
    class Meta:
        model = apps.get_model('fundraisers.Fundraiser')
        fields = '__all__'


class FundraiserDetailSerializer(FundraiserSerializer):
    
    pledges = PledgeSerializer(many=True, read_only=True)
    
    def update(self, instance, validated_data):
        
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

