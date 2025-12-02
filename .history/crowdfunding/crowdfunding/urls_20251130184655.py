"""
=============================================================================
URLS.PY - The Main URL Router (Project Level)
=============================================================================

WHAT IS THIS FILE?
------------------
This is the MAIN URL configuration for your Django project.
When a request comes in, Django starts here to figure out which 
view should handle it.

Think of this as the "front desk" of your application:
- Request arrives
- Front desk looks at the URL
- Directs it to the right department (app)

HOW URL ROUTING WORKS:
----------------------
1. User requests: GET /fundraisers/
2. Django checks ROOT_URLCONF in settings.py (points here)
3. Django tries to match the URL against patterns in urlpatterns
4. Match found: path('', include('fundraisers.urls'))
5. Django checks fundraisers/urls.py for 'fundraisers/'
6. Match found: path('fundraisers/', FundraiserList.as_view())
7. Django calls FundraiserList.get() method

URL PATTERN HIERARCHY:
----------------------
crowdfunding/urls.py (THIS FILE - project level)
    ├── /admin/         → Django admin panel
    ├── /               → fundraisers/urls.py
    │   ├── /fundraisers/       → FundraiserList
    │   ├── /fundraisers/<id>/  → FundraiserDetail
    │   └── /pledges/           → PledgeList
    ├── /               → users/urls.py
    │   ├── /users/             → CustomUserList
    │   └── /users/<id>/        → CustomUserDetail
    └── /api-token-auth/ → CustomAuthToken (login)

=============================================================================
"""

from django.contrib import admin
from django.urls import path, include
from users.views import CustomAuthToken


urlpatterns = [
    # =======================================================================
    # ADMIN PANEL
    # =======================================================================
    path("admin/", admin.site.urls),
    """
    DJANGO ADMIN PANEL
    ------------------
    URL: /admin/
    
    Django's built-in administration interface.
    
    FEATURES:
    - View, create, edit, delete database records
    - User management
    - Group and permission management
    - Automatically generated from your models
    
    TO ACCESS:
    1. Create a superuser: python manage.py createsuperuser
    2. Start server: python manage.py runserver
    3. Visit: http://localhost:8000/admin/
    4. Login with your superuser credentials
    
    TO ADD YOUR MODELS TO ADMIN:
    In fundraisers/admin.py:
        from django.contrib import admin
        from .models import Fundraiser, Pledge
        
        admin.site.register(Fundraiser)
        admin.site.register(Pledge)
    """
    
    # =======================================================================
    # APP URL INCLUDES
    # =======================================================================
    path('', include('fundraisers.urls')),
    """
    INCLUDE FUNDRAISERS APP URLS
    ----------------------------
    Pattern: '' (empty = start from root)
    
    include('fundraisers.urls') means:
    "Look in fundraisers/urls.py for more URL patterns"
    
    Since the pattern is '', the fundraisers URLs keep their paths:
    - /fundraisers/ (from fundraisers/urls.py)
    - /fundraisers/<id>/ (from fundraisers/urls.py)
    - /pledges/ (from fundraisers/urls.py)
    
    If we used path('api/', include('fundraisers.urls')), URLs would be:
    - /api/fundraisers/
    - /api/fundraisers/<id>/
    - /api/pledges/
    """
    
    path('', include('users.urls')),
    """
    INCLUDE USERS APP URLS
    ----------------------
    Pattern: '' (empty = start from root)
    
    include('users.urls') means:
    "Look in users/urls.py for more URL patterns"
    
    Provides:
    - /users/ (list all users, register new user)
    - /users/<id>/ (view specific user)
    
    NOTE: Both fundraisers and users have path('', ...) which means
    their URLs are at the root level. Django will try to match
    URLs in order, so the first matching pattern wins.
    """
    
    # =======================================================================
    # AUTHENTICATION ENDPOINT
    # =======================================================================
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    """
    TOKEN AUTHENTICATION ENDPOINT (LOGIN)
    -------------------------------------
    URL: /api-token-auth/
    View: CustomAuthToken
    Method: POST
    
    This is your LOGIN endpoint.
    
    HOW TO USE:
    -----------
    1. Send POST request with credentials:
       POST /api-token-auth/
       Body: {"username": "alice", "password": "secret123"}
    
    2. If valid, receive a response:
       {"token": "abc123...", "user_id": 1, "email": "alice@test.com"}
    
    3. Use the token in future requests:
       Authorization: Token abc123...
    
    WHY IS IT CALLED api-token-auth?
    --------------------------------
    This is a convention from Django REST Framework.
    You could name it anything:
    - path('login/', ...)
    - path('auth/token/', ...)
    - path('api/v1/login/', ...)
    
    WHAT IS name='api_token_auth'?
    ------------------------------
    This gives the URL pattern a name for reverse lookup.
    You can get the URL by name:
        from django.urls import reverse
        login_url = reverse('api_token_auth')  # Returns '/api-token-auth/'
    
    Useful for:
    - Templates: {% url 'api_token_auth' %}
    - Redirects: redirect('api_token_auth')
    - Documentation
    """
]


"""
=============================================================================
COMPLETE API REFERENCE
=============================================================================

AUTHENTICATION:
---------------
POST   /api-token-auth/          Login and get token
       Body: {"username": "...", "password": "..."}
       Returns: {"token": "...", "user_id": ..., "email": "..."}

USERS:
------
GET    /users/                   List all users
POST   /users/                   Register new user
       Body: {"username": "...", "password": "...", "email": "..."}
GET    /users/<id>/              View user details

FUNDRAISERS:
------------
GET    /fundraisers/             List all fundraisers
POST   /fundraisers/             Create fundraiser (requires auth)
       Header: Authorization: Token <your-token>
       Body: {"title": "...", "description": "...", "goal": ..., "image": "...", "is_open": true}
GET    /fundraisers/<id>/        View fundraiser with pledges
PUT    /fundraisers/<id>/        Update fundraiser (owner only)
       Header: Authorization: Token <your-token>
       Body: {"title": "new title", "goal": 5000}

PLEDGES:
--------
GET    /pledges/                 List all pledges
POST   /pledges/                 Create pledge
       Body: {"amount": ..., "comment": "...", "anonymous": false, "fundraiser": ..., "supporter": ...}

ADMIN:
------
GET    /admin/                   Django admin panel (superuser only)

=============================================================================
EXAMPLE WORKFLOW
=============================================================================

1. REGISTER A NEW USER:
   POST /users/
   Body: {"username": "alice", "password": "mypassword123", "email": "alice@test.com"}

2. LOGIN TO GET TOKEN:
   POST /api-token-auth/
   Body: {"username": "alice", "password": "mypassword123"}
   Response: {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b", ...}

3. CREATE A FUNDRAISER (with token):
   POST /fundraisers/
   Header: Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
   Body: {"title": "Build a School", "description": "Help us...", "goal": 50000, 
          "image": "https://example.com/school.jpg", "is_open": true}

4. VIEW THE FUNDRAISER:
   GET /fundraisers/1/

5. MAKE A PLEDGE:
   POST /pledges/
   Body: {"amount": 100, "comment": "Happy to help!", "anonymous": false,
          "fundraiser": 1, "supporter": 1}

6. VIEW FUNDRAISER WITH PLEDGES:
   GET /fundraisers/1/
   Response includes: {..., "pledges": [{...}]}

=============================================================================
"""
