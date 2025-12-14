from django.db import models
from django.contrib.auth import get_user_model

class Fundraiser(models.Model):
    
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.IntegerField()
    image = models.URLField()
    is_open = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='owned_fundraisers'
    )
    """
    ForeignKey: Creates a relationship to another model
    
    This says: "Every Fundraiser belongs to ONE User (the owner)"
    
    PARAMETERS EXPLAINED:
    ---------------------
    
    1. get_user_model()
       - Points to the CustomUser model
       - This is the "parent" in the relationship
    
    2. on_delete=models.CASCADE
       - What happens when the owner is deleted?
       - CASCADE means: delete all their fundraisers too
       - Other options:
         - PROTECT: Prevent deletion if they have fundraisers
         - SET_NULL: Set owner to NULL (requires null=True)
         - SET_DEFAULT: Set to a default value
    
    3. related_name='owned_fundraisers'
       - Allows reverse lookup from User to their Fundraisers
       - Without this, you'd use: user.fundraiser_set.all()
       - With this, you can use: user.owned_fundraisers.all()
    
    EXAMPLE USAGE:
    --------------
    # Get the owner of a fundraiser
    fundraiser.owner  → CustomUser object
    
    # Get all fundraisers by a user
    user.owned_fundraisers.all()  → QuerySet of Fundraisers
    
    IN THE DATABASE:
    ----------------
    This creates a column called 'owner_id' that stores the user's ID:
    
    Fundraiser Table:
    | id | title        | ... | owner_id |
    |----|--------------|-----|----------|
    | 1  | Build School | ... | 5        |  ← User #5 owns this fundraiser
    """


class Pledge(models.Model):
    """
    PLEDGE MODEL
    ============
    
    Represents a donation/pledge to a fundraiser.
    
    REAL-WORLD ANALOGY:
    -------------------
    Think of backing a Kickstarter project:
    - You pledge an amount of money
    - You might leave a comment
    - You can choose to be anonymous
    - Your pledge is linked to a specific project
    - Your pledge is linked to your account
    
    EXAMPLE DATA:
    -------------
    Pledge:
        amount: 100
        comment: "Great cause! Happy to help!"
        anonymous: False
        fundraiser: Fundraiser #1 (Build a School)
        supporter: User #3 (Bob)
    """
    
    amount = models.IntegerField()
    """
    The pledge amount in currency units (e.g., dollars)
    
    Example: 100 (meaning $100)
    """
    
    comment = models.CharField(max_length=200)
    """
    An optional message from the supporter
    
    Example: "Great cause! Happy to support!"
    """
    
    anonymous = models.BooleanField()
    """
    Whether to hide the supporter's identity
    
    - True: Show as "Anonymous" on the public page
    - False: Show the supporter's name
    
    NOTE: In the serializer/view, you'd check this before showing
    the supporter's info to the public
    """
    
    fundraiser = models.ForeignKey(
        'Fundraiser',
        on_delete=models.CASCADE,
        related_name='pledges'
    )
    """
    Links the pledge to a specific fundraiser
    
    WHY IS 'Fundraiser' IN QUOTES?
    ------------------------------
    Since Pledge is defined AFTER Fundraiser in this file, we could 
    reference it directly. But using a string ('Fundraiser') is a 
    safe practice that:
    - Avoids issues with class ordering
    - Works even if models are in different files
    
    related_name='pledges':
    - Allows: fundraiser.pledges.all() → All pledges for this fundraiser
    
    on_delete=CASCADE:
    - If a fundraiser is deleted, all its pledges are deleted too
    - This makes sense: pledges for a non-existent campaign are meaningless
    
    EXAMPLE:
    --------
    # Get the fundraiser a pledge belongs to
    pledge.fundraiser  → Fundraiser object
    
    # Get all pledges for a fundraiser
    fundraiser.pledges.all()  → QuerySet of Pledge objects
    
    # Calculate total pledged for a fundraiser
    fundraiser.pledges.aggregate(Sum('amount'))
    """
    
    supporter = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='pledges'
    )
    """
    Links the pledge to the user who made it
    
    related_name='pledges':
    - Allows: user.pledges.all() → All pledges made by this user
    
    on_delete=CASCADE:
    - If a user is deleted, their pledges are deleted too
    - Consider: Should we keep pledges even if user is deleted?
    - Alternative: on_delete=SET_NULL (requires null=True)
    
    EXAMPLE:
    --------
    # Get the user who made a pledge
    pledge.supporter  → CustomUser object
    
    # Get all pledges made by a user
    user.pledges.all()  → QuerySet of Pledge objects
    """

    is_hidden_by_owner = models.BooleanField(default=False)
    """
    Allows the fundraiser owner to hide/unhide the comment from public view.
    Default is False so existing pledges stay visible until explicitly hidden.
    """


