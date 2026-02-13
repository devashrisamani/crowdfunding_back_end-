from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .models import Fundraiser, Pledge
from .serializers import FundraiserSerializer, PledgeSerializer, FundraiserDetailSerializer, PledgeDetailSerializer
from .permissions import IsOwnerOrReadOnly, IsSupporterOrReadOnly, IsSupporterOrFundraiserOwnerOrReadOnly


class FundraiserList(APIView):
    """
    Handles listing all fundraisers and creating new fundraisers.
    """
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Return a list of all fundraisers.
        """
        fundraisers = Fundraiser.objects.all()
        serializer = FundraiserSerializer(fundraisers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Create a new fundraiser.
        The authenticated user is automatically set as the owner.
        """
        serializer = FundraiserSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(owner=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    


class FundraiserDetail(APIView):
    """
    Handles retrieve, update, and delete operations for a single fundraiser.
    """
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly  
    ]

    def get_object(self, pk):
        """
        Retrieve a fundraiser by primary key and
        check object-level permissions.
        """
    
        try:
            fundraiser = Fundraiser.objects.get(pk=pk)
            
            self.check_object_permissions(self.request, fundraiser)
            return fundraiser
            
        except Fundraiser.DoesNotExist:
            raise Http404
      
    def get(self, request, pk):
        """
        Retrieve a single fundraiser, including its pledges.
        """
        fundraiser = self.get_object(pk)
        
        serializer = FundraiserDetailSerializer(
            fundraiser,
            context={'request': request}
        )        
        return Response(serializer.data)


    def put(self, request, pk):
        """
        Update a fundraiser.
        Only the fundraiser owner may perform this action.
        """
        fundraiser = self.get_object(pk)

        serializer = FundraiserDetailSerializer(
            instance=fundraiser,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
  
    def delete(self,request,pk):
        """
        Delete a fundraiser.
        Only the owner may delete their fundraiser.
        """
        fundraiser = self.get_object(pk)
        fundraiser.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  

class PledgeList(APIView):
    """
    Handles listing all pledges and creating new pledges.
    """
    def get(self, request):
        """
        Return a list of all pledges.
        Comment visibility is handled by the serializer.
        """

        pledges = Pledge.objects.all()
        serializer = PledgeSerializer(
            pledges,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    def post(self, request):
        """
        Create a new pledge.
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

class PledgeDetail(APIView):
    """
    Handles retrieve and update operations for a single pledge.
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsSupporterOrFundraiserOwnerOrReadOnly  
    ]

    def get_object(self, pk):
        """
        Retrieve a pledge by primary key and
        check object-level permissions.
        """

        try:
            pledge = Pledge.objects.get(pk=pk)
            
            self.check_object_permissions(self.request, pledge)
            
            return pledge
            
        except Pledge.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Retrieve a single pledge.
        Comment visibility is handled by the serializer.
        """

        pledge = self.get_object(pk)
        
        serializer = PledgeDetailSerializer(
            pledge,
            context={'request': request}
        )
        
        return Response(serializer.data)

    def put(self,request, pk):
        """
        Update a pledge.
        Only the supporter who made the pledge may edit it.
        """

        pledge = self.get_object(pk)

        if request.user != pledge.supporter:
            return Response(
                {"detail": "Only the pledge supporter can edit this pledge."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PledgeDetailSerializer(
            instance=pledge,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        """
        Allow the fundraiser owner to hide or unhide a pledge comment.
        """
        pledge = self.get_object(pk)

        if request.user != pledge.fundraiser.owner:
            return Response(
                {"detail": "Only the fundraiser owner can hide or unhide comments."},
                status=status.HTTP_403_FORBIDDEN
            )

        if 'is_hidden_by_owner' not in request.data:
            return Response(
                {"detail": "Provide 'is_hidden_by_owner': true or false."},
                status=status.HTTP_400_BAD_REQUEST
            )

        raw_value = request.data.get('is_hidden_by_owner')
        if raw_value in [True, 'true', 'True', '1', 1]:
            pledge.is_hidden_by_owner = True
        elif raw_value in [False, 'false', 'False', '0', 0]:
            pledge.is_hidden_by_owner = False
        else:
            return Response(
                {"detail": "is_hidden_by_owner must be true or false."},
                status=status.HTTP_400_BAD_REQUEST
            )

        pledge.save()
        serializer = PledgeDetailSerializer(
            pledge,
            context={'request': request}
        )
        return Response(serializer.data)

from .serializers import CustomUserSerializer  