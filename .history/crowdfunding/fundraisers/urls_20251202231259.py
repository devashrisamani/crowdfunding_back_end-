"""
=============================================================================
URLS.PY - Fundraisers URL Router
=============================================================================

WHAT IS THIS FILE?
------------------
This file maps URLs to views for the fundraisers app.

URL PATTERNS DEFINED HERE:
--------------------------
| URL Pattern           | View              | HTTP Methods     |
|-----------------------|-------------------|------------------|
| /fundraisers/         | FundraiserList    | GET, POST        |
| /fundraisers/<id>/    | FundraiserDetail  | GET, PUT         |
| /pledges/             | PledgeList        | GET, POST        |

HOW URLS ARE CONNECTED:
-----------------------
1. Request arrives at Django (e.g., GET /fundraisers/)
2. Django checks crowdfunding/urls.py (root URL config)
3. It finds: path('', include('fundraisers.urls'))
4. Django checks THIS file for a match
5. It matches 'fundraisers/' and calls FundraiserList.as_view()

=============================================================================
"""

from django.urls import path
from . import views
# from . import views means "import views.py from this same folder"


urlpatterns = [
    # =======================================================================
    # FUNDRAISER ENDPOINTS
    # =======================================================================
    
    path('fundraisers/', views.FundraiserList.as_view()),
    # """
    # FUNDRAISER LIST ENDPOINT
    # ------------------------
    # URL: /fundraisers/
    # View: FundraiserList
    
    # GET /fundraisers/
    #     → Returns a list of all fundraisers
    #     → Example: [{"id": 1, "title": "..."}, {"id": 2, "title": "..."}]
    
    # POST /fundraisers/
    #     → Creates a new fundraiser
    #     → Requires authentication
    #     → Body: {"title": "...", "description": "...", "goal": 50000, ...}
    #     → Returns: The created fundraiser
    # """
    
    path('fundraisers/<int:pk>/', views.FundraiserDetail.as_view()),
    # """
    # FUNDRAISER DETAIL ENDPOINT
    # --------------------------
    # URL: /fundraisers/<id>/
    # View: FundraiserDetail
    
    # <int:pk> captures a number from the URL:
    # - /fundraisers/1/  →  pk = 1
    # - /fundraisers/42/ →  pk = 42
    
    # GET /fundraisers/1/
    #     → Returns details of fundraiser #1
    #     → Includes nested pledges
    #     → Example: {"id": 1, "title": "...", "pledges": [...]}
    
    # PUT /fundraisers/1/
    #     → Updates fundraiser #1
    #     → Requires authentication + must be owner
    #     → Body: {"title": "New title", "goal": 60000}
    #     → Returns: The updated fundraiser
    # """
    
    # =======================================================================
    # PLEDGE ENDPOINTS
    # =======================================================================
    
    path('pledges/', views.PledgeList.as_view())
    # """
    # PLEDGE LIST ENDPOINT
    # --------------------
    # URL: /pledges/
    # View: PledgeList
    
    # GET /pledges/
    #     → Returns a list of all pledges
    #     → Example: [{"id": 1, "amount": 100}, {"id": 2, "amount": 250}]
    
    # POST /pledges/
    #     → Creates a new pledge
    #     → Body: {"amount": 100, "comment": "...", "fundraiser": 1, "supporter": 3}
    #     → Returns: The created pledge
    
    # IMPROVEMENT IDEAS:
    # ------------------
    # You might want to add:
    # - /pledges/<int:pk>/  →  View/update/delete a specific pledge
    # - /fundraisers/<int:pk>/pledges/  →  Pledges for a specific fundraiser
    # """
     path('pledges/<int:pk>/', views.PledgeDetail.as_view())
]


"""
=============================================================================
API ENDPOINTS SUMMARY
=============================================================================

FUNDRAISERS:
------------
GET    /fundraisers/          List all fundraisers (public)
POST   /fundraisers/          Create fundraiser (authenticated)
GET    /fundraisers/<id>/     View fundraiser details (public)
PUT    /fundraisers/<id>/     Update fundraiser (owner only)

PLEDGES:
--------
GET    /pledges/              List all pledges (public)
POST   /pledges/              Create pledge (currently public - should require auth)

USERS (defined in users/urls.py):
---------------------------------
GET    /users/                List all users
POST   /users/                Register new user
GET    /users/<id>/           View user details

AUTHENTICATION (defined in crowdfunding/urls.py):
-------------------------------------------------
POST   /api-token-auth/       Login and get token

=============================================================================
TESTING YOUR API
=============================================================================

Using curl:
-----------
# List fundraisers
curl http://localhost:8000/fundraisers/

# Create user (register)
curl -X POST http://localhost:8000/users/ \
     -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "secret123", "email": "alice@test.com"}'

# Login (get token)
curl -X POST http://localhost:8000/api-token-auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "secret123"}'

# Create fundraiser (with token)
curl -X POST http://localhost:8000/fundraisers/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Token YOUR_TOKEN_HERE" \
     -d '{"title": "My Project", "description": "...", "goal": 1000, "image": "http://...", "is_open": true}'

Using HTTPie (simpler syntax):
------------------------------
# List fundraisers
http GET http://localhost:8000/fundraisers/

# Create user
http POST http://localhost:8000/users/ username=alice password=secret123 email=alice@test.com

# Login
http POST http://localhost:8000/api-token-auth/ username=alice password=secret123

# Create fundraiser
http POST http://localhost:8000/fundraisers/ \
     Authorization:"Token YOUR_TOKEN_HERE" \
     title="My Project" description="..." goal:=1000 image="http://..." is_open:=true

Using Insomnia/Postman:
-----------------------
These GUI tools let you easily:
- Set headers (Authorization: Token xxx)
- Send JSON bodies
- Save and organize requests

=============================================================================
"""
