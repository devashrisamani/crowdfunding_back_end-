"""
=============================================================================
MODELS.PY - The Database Blueprint for Users
=============================================================================

WHAT IS THIS FILE?
------------------
This file defines the "shape" of your data - what information you want to 
store about users. Think of it like designing a spreadsheet: you decide 
what columns (fields) you need.

WHY DO WE NEED THIS?
--------------------
Django comes with a built-in User model, but we often need to customize it.
By creating a CustomUser, we can add extra fields later (like profile picture,
bio, etc.) without breaking our database.

WHEN DOES THIS RUN?
-------------------
1. When you run `python manage.py makemigrations` - Django reads this file
   and creates migration files (instructions to build the database tables)
2. When you run `python manage.py migrate` - Django executes those instructions
   and creates/updates the actual database tables
3. Whenever your code interacts with user data (creating users, logging in, etc.)

ORDER IN THE REQUEST FLOW:
--------------------------
This file is Step 1 in the architecture - it defines what data CAN exist.
The actual creation/retrieval of users happens in views.py using these models.

=============================================================================
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    CUSTOM USER MODEL
    =================
    
    This is our user model that extends Django's built-in AbstractUser.
    
    WHAT IS AbstractUser?
    ---------------------
    AbstractUser is Django's template for a user. It already includes:
    - username (required, unique)
    - password (automatically hashed/encrypted for security)
    - email
    - first_name
    - last_name
    - is_active (can this user log in?)
    - is_staff (can access admin panel?)
    - is_superuser (has all permissions?)
    - date_joined
    - last_login
    
    WHY EXTEND IT?
    --------------
    Even if we don't add extra fields now, creating a CustomUser from the 
    start is a Django best practice. If you later want to add fields like:
    - profile_picture
    - bio
    - phone_number
    
    You can simply add them here without complex database migrations.
    
    EXAMPLE - Adding a field later:
    --------------------------------
    class CustomUser(AbstractUser):
        bio = models.TextField(blank=True)  # Optional bio field
        profile_picture = models.URLField(blank=True)  # Optional image URL
    
    IMPORTANT: 
    ----------
    In settings.py, we tell Django to use this model instead of the default:
    AUTH_USER_MODEL = 'users.CustomUser'
    """
    
    def __str__(self):
        """
        THE __str__ METHOD
        ------------------
        This is a "magic method" that Python calls when you try to convert
        an object to a string. 
        
        When does this happen?
        - In the Django admin panel (shows username instead of "CustomUser object (1)")
        - When you print a user: print(user) → "john_doe"
        - In dropdown menus that list users
        
        Without this method, you'd see ugly text like "CustomUser object (1)"
        instead of the actual username.
        """
        return self.username
