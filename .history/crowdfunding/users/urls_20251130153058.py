"""
=============================================================================
URLS.PY - The URL Router (Traffic Director)
=============================================================================

WHAT IS THIS FILE?
------------------
This file maps URLs to views. When someone visits your website, Django
looks at the URL and decides which view function/class should handle it.

Think of it like a phone directory:
- URL pattern → View to call
- /users/ → CustomUserList
- /users/1/ → CustomUserDetail

WHY IS THIS SEPARATE FROM views.py?
-----------------------------------
Separation of concerns:
- urls.py handles ROUTING (which URL goes where)
- views.py handles LOGIC (what to do when you get there)

This makes code cleaner and easier to maintain. You can look at urls.py
to see all available endpoints at a glance.

HOW DOES URL ROUTING WORK?
--------------------------
1. Request comes in: GET /users/
2. Django checks crowdfunding/urls.py (ROOT_URLCONF in settings)
3. It finds: path('', include('users.urls'))
4. Django then checks THIS file (users/urls.py)
5. It matches 'users/' and calls CustomUserList.as_view()

ORDER IN THE REQUEST FLOW:
--------------------------
This is Step 2 - after the request arrives but before the view runs.

1. HTTP Request arrives (GET /users/)
2. → urls.py matches the pattern ← WE ARE HERE
3. → views.py handles the logic
4. → Response sent back

=============================================================================
"""

from django.urls import path
from . import views
# from . import views means "import views from the current package (folder)"
# The dot (.) refers to the current directory (users/)


urlpatterns = [
    # =======================================================================
    # USER LIST ENDPOINT
    # =======================================================================
    path('users/', views.CustomUserList.as_view()),
    # 
    # WHAT THIS MEANS:
    # ----------------
    # - 'users/' is the URL pattern to match
    # - views.CustomUserList is the view class to handle it
    # - .as_view() converts the class into a callable view function
    #
    # SUPPORTED METHODS:
    # ------------------
    # - GET /users/  → List all users
    # - POST /users/ → Create a new user (registration)
    #
    # EXAMPLE REQUESTS:
    # -----------------
    # GET http://localhost:8000/users/
    #     Returns: [{"id": 1, "username": "alice"}, {"id": 2, "username": "bob"}]
    #
    # POST http://localhost:8000/users/
    #     Body: {"username": "charlie", "password": "secret123", "email": "c@test.com"}
    #     Returns: {"id": 3, "username": "charlie", "email": "c@test.com"}
    
    # =======================================================================
    # USER DETAIL ENDPOINT
    # =======================================================================
    path('users/<int:pk>/', views.CustomUserDetail.as_view()),
    #
    # WHAT THIS MEANS:
    # ----------------
    # - 'users/<int:pk>/' is the URL pattern
    # - <int:pk> is a "URL parameter" - it captures a number from the URL
    # - <int:pk> means: capture an integer and pass it to the view as 'pk'
    #
    # WHAT IS pk?
    # -----------
    # pk stands for "primary key" - the unique identifier for a database record
    # In our case, it's the user's ID number
    #
    # HOW URL PARAMETERS WORK:
    # ------------------------
    # URL: /users/42/
    # Pattern: users/<int:pk>/
    # Result: pk = 42 is passed to the view's get(request, pk) method
    #
    # SUPPORTED METHODS:
    # ------------------
    # - GET /users/1/ → Get details of user with id=1
    #
    # EXAMPLE REQUEST:
    # ----------------
    # GET http://localhost:8000/users/1/
    #     Returns: {"id": 1, "username": "alice", "email": "alice@test.com"}
]

"""
URL PATTERN SYNTAX CHEAT SHEET:
===============================

BASIC PATTERNS:
---------------
path('about/', view)           → matches /about/
path('contact/', view)         → matches /contact/

PARAMETERS:
-----------
<int:pk>      → Captures an integer: /users/42/ → pk=42
<str:name>    → Captures a string: /users/alice/ → name='alice'
<slug:slug>   → Captures a slug: /posts/my-post/ → slug='my-post'
<uuid:id>     → Captures a UUID: /items/550e8400-e29b-41d4-a716-446655440000/

EXAMPLES:
---------
path('posts/<int:year>/<int:month>/', view)
    → /posts/2024/03/ → year=2024, month=3

path('users/<str:username>/profile/', view)  
    → /users/alice/profile/ → username='alice'

WHY USE as_view()?
==================
Django REST Framework's APIView is a CLASS, but Django's URL routing 
expects a FUNCTION. The as_view() method converts the class into a 
callable function that Django can work with.

What as_view() does:
1. Creates an instance of the class
2. Calls the appropriate method (get, post, etc.) based on HTTP method
3. Returns the response
"""
