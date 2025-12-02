"""
=============================================================================
MODELS.PY - The Database Blueprint for Fundraisers & Pledges
=============================================================================

WHAT IS THIS FILE?
------------------
This file defines the data structure for the core crowdfunding features:
- Fundraisers (the campaigns people create to raise money)
- Pledges (the donations people make to support campaigns)

Think of models as spreadsheet designs:
- Each class = a table
- Each field = a column
- Each instance = a row

HOW DO MODELS RELATE TO EACH OTHER?
------------------------------------
    CustomUser (owner)           CustomUser (supporter)
         |                              |
         | creates                      | makes
         |                              |
         v                              v
    Fundraiser ←──── Pledge ────────────┘
         
One User can create MANY Fundraisers (one-to-many)
One Fundraiser can have MANY Pledges (one-to-many)
One User can make MANY Pledges (one-to-many)

DATABASE RELATIONSHIPS:
-----------------------
These relationships are created using ForeignKey fields, which create
a "link" between tables in the database.

WHEN DOES THIS RUN?
-------------------
1. makemigrations - Django reads this file and creates migration files
2. migrate - Django creates/updates database tables
3. Whenever code creates, reads, updates, or deletes fundraisers/pledges

=============================================================================
"""

from django.db import models
from django.contrib.auth import get_user_model
# get_user_model() is a function that returns whatever user model is 
# configured in settings.py (AUTH_USER_MODEL = 'users.CustomUser')
# This is better than importing CustomUser directly because:
# - It avoids circular imports
# - It works even if you change your user model later


class Fundraiser(models.Model):
    """
    FUNDRAISER MODEL
    ================
    
    Represents a crowdfunding campaign/project.
    
    REAL-WORLD ANALOGY:
    -------------------
    Think of a GoFundMe or Kickstarter campaign:
    - Has a title and description
    - Has a monetary goal
    - Has an image
    - Can be open (accepting pledges) or closed
    - Was created by someone (the owner)
    
    EXAMPLE DATA:
    -------------
    Fundraiser:
        title: "Help Me Build a School"
        description: "We're raising funds to build a primary school..."
        goal: 50000
        image: "https://example.com/school.jpg"
        is_open: True
        date_created: 2024-03-15 10:30:00
        owner: User #1 (Alice)
    """
    
    # =========================================================================
    # BASIC TEXT FIELDS
    # =========================================================================
    
    title = models.CharField(max_length=200)
    """
    CharField: A short text field with a maximum length
    
    - max_length=200 means titles can be up to 200 characters
    - Good for short text like names, titles, labels
    - In the database, this becomes VARCHAR(200)
    
    Example: "Help Me Build a School"
    """
    
    description = models.TextField()
    """
    TextField: A long text field with no practical limit
    
    - Use for longer content like descriptions, articles, comments
    - No max_length required (unlimited text)
    - In the database, this becomes TEXT
    
    Example: "We're raising funds to build a primary school in a rural 
              village. The school will provide education for over 200 
              children who currently have no access to learning..."
    """
    
    # =========================================================================
    # NUMBER FIELD
    # =========================================================================
    
    goal = models.IntegerField()
    """
    IntegerField: A whole number (no decimals)
    
    - Stores the fundraising goal in your currency unit (e.g., dollars)
    - For money with decimals, you'd use DecimalField instead
    - In the database, this becomes INTEGER
    
    Example: 50000 (meaning $50,000)
    
    NOTE: For real financial apps, DecimalField is better:
    goal = models.DecimalField(max_digits=10, decimal_places=2)
    This would allow: 50000.00
    """
    
    # =========================================================================
    # URL FIELD
    # =========================================================================
    
    image = models.URLField()
    """
    URLField: A special CharField that validates URLs
    
    - Ensures the value is a valid URL format
    - Stores the web address of an image
    - In the database, this is VARCHAR(200) by default
    
    Example: "https://example.com/images/school-project.jpg"
    
    NOTE: For file uploads, you'd use ImageField instead:
    image = models.ImageField(upload_to='fundraiser_images/')
    """
    
    # =========================================================================
    # BOOLEAN FIELD
    # =========================================================================
    
    is_open = models.BooleanField()
    """
    BooleanField: A True/False field
    
    - Only two possible values: True or False
    - Controls whether the fundraiser is accepting pledges
    - In the database, this becomes BOOLEAN or TINYINT(1)
    
    Example: True (campaign is open for pledges)
             False (campaign has ended or is paused)
    
    TIP: You could add a default:
    is_open = models.BooleanField(default=True)
    """
    
    # =========================================================================
    # DATE/TIME FIELD
    # =========================================================================
    
    date_created = models.DateTimeField(auto_now_add=True)
    """
    DateTimeField: Stores date AND time
    
    - auto_now_add=True means it automatically sets to the current 
      date/time when the object is FIRST created
    - You never need to set this manually - Django does it for you
    - In the database, this becomes DATETIME
    
    Example: 2024-03-15 10:30:45.123456
    
    SIMILAR OPTIONS:
    - auto_now=True: Updates to current time on EVERY save (good for "last_modified")
    - auto_now_add=True: Only sets on creation (good for "date_created")
    - Neither: You must set it manually
    """
    
    # =========================================================================
    # RELATIONSHIP FIELD (Foreign Key)
    # =========================================================================
    
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


"""
=============================================================================
MODEL RELATIONSHIPS SUMMARY
=============================================================================

               ┌─────────────┐
               │ CustomUser  │
               └─────────────┘
                    │    │
         owns ──────┘    └────── supports
                │                    │
                ▼                    ▼
        ┌─────────────┐      ┌─────────────┐
        │ Fundraiser  │◄─────│   Pledge    │
        └─────────────┘      └─────────────┘
              1         has many      ∞

RELATIONSHIP TYPES:
-------------------
1. One-to-Many: User → Fundraiser (one user can create many fundraisers)
2. One-to-Many: User → Pledge (one user can make many pledges)
3. One-to-Many: Fundraiser → Pledge (one fundraiser can have many pledges)

HOW TO QUERY RELATIONSHIPS:
---------------------------
# Forward (from child to parent)
pledge.fundraiser          → The fundraiser this pledge is for
pledge.supporter           → The user who made this pledge
fundraiser.owner           → The user who created this fundraiser

# Reverse (from parent to children) - uses related_name
user.owned_fundraisers.all()   → All fundraisers created by this user
user.pledges.all()             → All pledges made by this user
fundraiser.pledges.all()       → All pledges for this fundraiser

=============================================================================
"""
