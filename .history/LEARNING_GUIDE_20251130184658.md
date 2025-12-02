# 🎓 Django REST Framework Learning Guide

## Welcome to Your Crowdfunding API!

This guide will help you understand how all the pieces of your Django project fit together. By the end, you'll understand exactly what happens when someone uses your API.

---

## 📁 Project Structure Overview

```
crowdfunding_back_end/
├── crowdfunding/                   # The main Django project folder
│   ├── crowdfunding/               # Project configuration
│   │   ├── settings.py             # All project settings
│   │   ├── urls.py                 # Main URL router
│   │   ├── wsgi.py                 # Production server entry point
│   │   └── asgi.py                 # Async server entry point
│   │
│   ├── fundraisers/                # App for fundraisers & pledges
│   │   ├── models.py               # Database tables (Fundraiser, Pledge)
│   │   ├── serializers.py          # JSON ↔ Python converters
│   │   ├── views.py                # Request handlers (logic)
│   │   ├── urls.py                 # URL routes for this app
│   │   ├── permissions.py          # Who can do what
│   │   └── admin.py                # Admin panel config
│   │
│   ├── users/                      # App for user management
│   │   ├── models.py               # CustomUser model
│   │   ├── serializers.py          # User JSON converter
│   │   ├── views.py                # User request handlers
│   │   └── urls.py                 # User URL routes
│   │
│   ├── db.sqlite3                  # The database file
│   └── manage.py                   # Django command-line tool
│
├── requirements.txt                # Python packages needed
├── Procfile                        # Deployment config
└── README.md                       # Project description
```

---

## 🔄 How a Request Flows Through Django

When someone makes an API request, here's exactly what happens:

```
┌─────────────────────────────────────────────────────────────────┐
│                        THE REQUEST JOURNEY                       │
└─────────────────────────────────────────────────────────────────┘

    🌐 User's Browser/App
           │
           │  HTTP Request: GET /fundraisers/1/
           ▼
    ┌──────────────────┐
    │   1. DJANGO      │  Django receives the request
    │   Web Server     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   2. MIDDLEWARE  │  Each middleware processes the request
    │   (settings.py)  │  Authentication, CORS, Security, etc.
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   3. URL ROUTER  │  crowdfunding/urls.py looks at the URL
    │   (urls.py)      │  Matches pattern, finds the right view
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   4. VIEW        │  FundraiserDetail.get() runs
    │   (views.py)     │  Handles the business logic
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   5. MODEL       │  Fundraiser.objects.get(pk=1)
    │   (models.py)    │  Queries the database
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   6. DATABASE    │  SQLite returns the data
    │   (db.sqlite3)   │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   7. SERIALIZER  │  FundraiserDetailSerializer
    │   (serializers)  │  Converts Python object → JSON
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   8. RESPONSE    │  JSON sent back to user
    │   HTTP 200 OK    │
    └──────────────────┘
           │
           ▼
    🌐 User's Browser/App receives:
    {
        "id": 1,
        "title": "Build a School",
        "description": "...",
        "pledges": [...]
    }
```

---

## 📚 File-by-File Explanation

### 🔧 Step 1: Settings (`crowdfunding/settings.py`)

**Purpose:** The control center. Configures everything about your Django project.

**Key Settings:**
| Setting | What It Does |
|---------|--------------|
| `INSTALLED_APPS` | List of apps Django knows about |
| `DATABASES` | How to connect to the database |
| `AUTH_USER_MODEL` | Which model to use for users |
| `REST_FRAMEWORK` | How API authentication works |
| `MIDDLEWARE` | Functions that process every request |

**When It's Read:** Once, when Django starts up.

---

### 🛣️ Step 2: URL Routing (`urls.py` files)

**Purpose:** Maps URLs to views. Like a phone directory for your app.

**Main Router (`crowdfunding/urls.py`):**

```
/admin/           → Django Admin Panel
/                 → Include fundraisers URLs
/                 → Include users URLs
/api-token-auth/  → Login endpoint
```

**Fundraisers Router (`fundraisers/urls.py`):**

```
/fundraisers/         → FundraiserList (list all, create new)
/fundraisers/<id>/    → FundraiserDetail (view one, update)
/pledges/             → PledgeList (list all, create new)
```

**Users Router (`users/urls.py`):**

```
/users/           → CustomUserList (list all, register)
/users/<id>/      → CustomUserDetail (view one)
```

---

### 📊 Step 3: Models (`models.py` files)

**Purpose:** Define the structure of your database tables.

**The User Model (`users/models.py`):**

```python
CustomUser
├── username (inherited from AbstractUser)
├── password (inherited, auto-hashed)
├── email (inherited)
├── first_name (inherited)
├── last_name (inherited)
└── ... other inherited fields
```

**The Fundraiser Model (`fundraisers/models.py`):**

```python
Fundraiser
├── id (auto-created)
├── title (CharField)
├── description (TextField)
├── goal (IntegerField)
├── image (URLField)
├── is_open (BooleanField)
├── date_created (DateTimeField, auto-set)
└── owner (ForeignKey → CustomUser)
```

**The Pledge Model (`fundraisers/models.py`):**

```python
Pledge
├── id (auto-created)
├── amount (IntegerField)
├── comment (CharField)
├── anonymous (BooleanField)
├── fundraiser (ForeignKey → Fundraiser)
└── supporter (ForeignKey → CustomUser)
```

**Relationship Diagram:**

```
CustomUser ──────┬──────── owns ────────▶ Fundraiser
                 │                              ▲
                 │                              │
                 └──────── supports ────▶ Pledge ┘
```

---

### 🔄 Step 4: Serializers (`serializers.py` files)

**Purpose:** Translate between Python objects and JSON.

**Why We Need Them:**

- Database stores Python objects
- APIs communicate via JSON
- Serializers convert between the two!

**The Translation Process:**

```
SERIALIZATION (sending data OUT):
Python Object → Serializer → JSON Dictionary → HTTP Response

DESERIALIZATION (receiving data IN):
HTTP Request → JSON Dictionary → Serializer → Python Object → Database
```

**Types of Serializers:**
| Serializer | Used For |
|------------|----------|
| `PledgeSerializer` | All pledge operations |
| `FundraiserSerializer` | Listing fundraisers |
| `FundraiserDetailSerializer` | Single fundraiser with pledges |
| `CustomUserSerializer` | All user operations |

---

### 🧠 Step 5: Views (`views.py` files)

**Purpose:** Handle requests and return responses. The "brain" of your app.

**What Views Do:**

1. Receive an HTTP request
2. Check permissions (is user allowed?)
3. Query the database (via models)
4. Process the data (via serializers)
5. Return an HTTP response

**View Methods:**
| HTTP Method | View Method | Purpose |
|-------------|-------------|---------|
| GET | `get()` | Retrieve data |
| POST | `post()` | Create new data |
| PUT | `put()` | Update existing data |
| DELETE | `delete()` | Remove data |

---

### 🔒 Step 6: Permissions (`permissions.py`)

**Purpose:** Control who can access what.

**Built-in Permissions:**
| Permission | Who Can Access |
|------------|----------------|
| `AllowAny` | Everyone |
| `IsAuthenticated` | Logged-in users only |
| `IsAuthenticatedOrReadOnly` | Anyone reads, logged-in writes |
| `IsAdminUser` | Admin users only |

**Custom Permission (`IsOwnerOrReadOnly`):**

- Anyone can VIEW (read)
- Only the OWNER can EDIT (write)

---

## 🎬 Complete Request Examples

### Example 1: Creating a User (Registration)

```
POST /users/
Body: {"username": "alice", "password": "secret123", "email": "alice@test.com"}
```

**What Happens:**

1. Request arrives at Django
2. URL matches `/users/` → `CustomUserList.post()`
3. View creates `CustomUserSerializer(data=request.data)`
4. Serializer validates the data
5. Serializer calls `create_user()` (hashes password)
6. User saved to database
7. Response: `201 Created` with user data

---

### Example 2: Logging In

```
POST /api-token-auth/
Body: {"username": "alice", "password": "secret123"}
```

**What Happens:**

1. Request arrives at Django
2. URL matches `/api-token-auth/` → `CustomAuthToken.post()`
3. Built-in serializer validates credentials
4. `Token.objects.get_or_create(user=user)` gets/creates token
5. Response: `{"token": "abc123...", "user_id": 1, "email": "alice@test.com"}`

**After Login:**
Include token in future requests:

```
Authorization: Token abc123...
```

---

### Example 3: Creating a Fundraiser

```
POST /fundraisers/
Headers: Authorization: Token abc123...
Body: {
    "title": "Build a School",
    "description": "We need your help...",
    "goal": 50000,
    "image": "https://example.com/school.jpg",
    "is_open": true
}
```

**What Happens:**

1. Request arrives at Django
2. `TokenAuthentication` reads the token
3. `request.user` is set to Alice
4. URL matches `/fundraisers/` → `FundraiserList.post()`
5. `IsAuthenticatedOrReadOnly` checks: Is user logged in? ✓
6. View creates serializer with request data
7. Serializer validates the data
8. `serializer.save(owner=request.user)` - sets Alice as owner
9. Fundraiser saved to database
10. Response: `201 Created` with fundraiser data

---

### Example 4: Viewing a Fundraiser

```
GET /fundraisers/1/
```

**What Happens:**

1. Request arrives at Django
2. URL matches `/fundraisers/<int:pk>/` → `FundraiserDetail.get()`
3. `pk=1` is extracted from URL
4. `Fundraiser.objects.get(pk=1)` queries database
5. `FundraiserDetailSerializer(fundraiser)` converts to JSON
6. Includes nested pledges (from `related_name='pledges'`)
7. Response: `200 OK` with fundraiser + pledges

---

### Example 5: Making a Pledge

```
POST /pledges/
Body: {
    "amount": 100,
    "comment": "Happy to help!",
    "anonymous": false,
    "fundraiser": 1,
    "supporter": 2
}
```

**What Happens:**

1. Request arrives at Django
2. URL matches `/pledges/` → `PledgeList.post()`
3. View creates `PledgeSerializer(data=request.data)`
4. Serializer validates (checks fundraiser #1 exists, etc.)
5. Pledge saved to database
6. Response: `201 Created` with pledge data

---

## 🧪 Testing Your API

### Using cURL (Command Line)

```bash
# Register a user
curl -X POST http://localhost:8000/users/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass123", "email": "test@test.com"}'

# Login
curl -X POST http://localhost:8000/api-token-auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass123"}'

# List fundraisers (no auth needed)
curl http://localhost:8000/fundraisers/

# Create fundraiser (auth required)
curl -X POST http://localhost:8000/fundraisers/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Token YOUR_TOKEN_HERE" \
     -d '{"title": "My Project", "description": "Description here", "goal": 1000, "image": "http://example.com/img.jpg", "is_open": true}'
```

### Using the DRF Browsable API

1. Start the server: `python manage.py runserver`
2. Visit `http://localhost:8000/fundraisers/` in your browser
3. You'll see a nice interface to test your API!

---

## 🔑 Key Concepts Summary

| Concept         | One-Sentence Explanation                                   |
| --------------- | ---------------------------------------------------------- |
| **Model**       | Defines what data you can store (database table structure) |
| **Serializer**  | Converts between Python objects and JSON                   |
| **View**        | Handles requests and decides what to do with them          |
| **URL Pattern** | Maps a URL to a specific view                              |
| **Permission**  | Decides who can access what                                |
| **Token**       | A secret key users get after logging in to prove identity  |
| **Migration**   | Instructions to create/update database tables from models  |
| **ForeignKey**  | A field that links to another model (relationship)         |
| **QuerySet**    | A list of database objects that you can filter             |

---

## 📖 Reading Order for Understanding

If you're new to Django REST Framework, read the files in this order:

1. **`settings.py`** - Understand the configuration
2. **`users/models.py`** - See how users are defined
3. **`users/serializers.py`** - See how users become JSON
4. **`users/views.py`** - See how user requests are handled
5. **`users/urls.py`** - See how URLs route to views
6. **`fundraisers/models.py`** - See the main data models
7. **`fundraisers/serializers.py`** - See data conversion
8. **`fundraisers/permissions.py`** - See access control
9. **`fundraisers/views.py`** - See request handling
10. **`fundraisers/urls.py`** - See the complete URL structure
11. **`crowdfunding/urls.py`** - See how it all connects

---

## 🚀 Next Steps

Now that you understand the basics, try:

1. **Add a new field** to Fundraiser (like `location`)
2. **Add a new endpoint** (like `DELETE /fundraisers/<id>/`)
3. **Add filtering** (like `GET /fundraisers/?is_open=true`)
4. **Improve security** (auto-set `supporter` from `request.user`)
5. **Add more validation** (pledge amount must be positive)
