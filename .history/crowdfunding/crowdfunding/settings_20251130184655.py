"""
=============================================================================
SETTINGS.PY - The Configuration Hub of Your Django Project
=============================================================================

WHAT IS THIS FILE?
------------------
This is the CENTRAL CONFIGURATION file for your entire Django project.
Every setting that controls Django's behavior is defined here.

Think of it as the "control panel" for your application:
- Database connections
- Security settings
- Installed apps
- Middleware
- Static files
- And much more!

WHEN IS THIS FILE USED?
-----------------------
Django reads this file when the server starts. Changes here usually
require a server restart to take effect.

HOW DO I FIND THIS FILE?
------------------------
Django knows to look here because of:
- The DJANGO_SETTINGS_MODULE environment variable
- Or the settings parameter in manage.py

=============================================================================
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from a .env file (if it exists)
load_dotenv("../.env")
"""
WHAT IS dotenv?
---------------
Environment variables are settings stored OUTSIDE your code.
This is important for:
- Security: Don't commit secret keys to git!
- Flexibility: Different values for development vs production

A .env file might look like:
    DJANGO_SECRET_KEY=super-secret-key-here
    DJANGO_DEBUG=False
    DATABASE_URL=postgres://user:pass@host:5432/dbname

load_dotenv() reads these and makes them available via os.environ
"""


# =============================================================================
# BASE DIRECTORY
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
"""
BASE_DIR: The root directory of your Django project

Path(__file__) → Path to this settings.py file
.resolve() → Get the absolute path
.parent.parent → Go up two directories (crowdfunding/crowdfunding/ → crowdfunding/)

This gives you: /path/to/your/project/crowdfunding/

Used throughout settings to build paths like:
    BASE_DIR / "db.sqlite3" → /path/to/project/crowdfunding/db.sqlite3
"""


# =============================================================================
# SECURITY SETTINGS
# =============================================================================

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-t=t+f2@6ekpry$z4xvgodd6(dh_@yycvy*-pie-4ipk(%kgksf'
)
"""
SECRET_KEY: A unique, secret string used for cryptographic signing

WHAT IT'S USED FOR:
- Signing session cookies
- Protecting against CSRF attacks  
- Generating password reset tokens
- Any cryptographic signing

SECURITY RULES:
1. NEVER commit your production secret key to git!
2. Use a different key for production than development
3. Make it long and random (50+ characters)

HOW THIS CODE WORKS:
- os.environ.get('DJANGO_SECRET_KEY', 'fallback')
- First, tries to get from environment variable
- If not found, uses the fallback value (for development only!)

FOR PRODUCTION:
Set DJANGO_SECRET_KEY environment variable on your server.
"""


DEBUG = os.environ.get('DJANGO_DEBUG') != 'False'
"""
DEBUG MODE: Enables detailed error pages and extra logging

DEBUG = True (Development):
- Shows detailed error pages with tracebacks
- Logs all SQL queries
- Serves static files automatically
- NEVER use in production! Exposes sensitive info.

DEBUG = False (Production):
- Shows generic error pages
- Better performance
- More secure

HOW THIS CODE WORKS:
- If DJANGO_DEBUG is not set → None != 'False' → True
- If DJANGO_DEBUG is 'False' → 'False' != 'False' → False
- If DJANGO_DEBUG is anything else → True
"""


ALLOWED_HOSTS = ['*']
"""
ALLOWED_HOSTS: Which domain names can serve this Django site

['*'] means ALL domains are allowed - good for development, risky for production.

FOR PRODUCTION, be specific:
ALLOWED_HOSTS = ['mysite.com', 'www.mysite.com', 'api.mysite.com']

This prevents HTTP Host header attacks.
"""


CORS_ORIGIN_ALLOW_ALL = True
"""
CORS (Cross-Origin Resource Sharing)

WHAT IS CORS?
By default, web browsers block requests from one domain to another.
If your frontend is at mysite.com and API is at api.mysite.com,
the browser would block the API requests without CORS headers.

CORS_ORIGIN_ALLOW_ALL = True:
- Allows ANY website to make requests to your API
- Good for development and public APIs
- Be careful in production!

FOR MORE CONTROL:
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS = [
    'https://mysite.com',
    'https://www.mysite.com',
]
"""


# =============================================================================
# INSTALLED APPS
# =============================================================================

INSTALLED_APPS = [
    # YOUR APPS (custom apps you created)
    'fundraisers.apps.FundraisersConfig',   # The main crowdfunding app
    'users.apps.UsersConfig',                # Custom user management
    
    # THIRD-PARTY APPS (installed via pip)
    'rest_framework',                        # Django REST Framework for APIs
    'rest_framework.authtoken',              # Token authentication
    'corsheaders',                           # Handle CORS headers
    
    # DJANGO BUILT-IN APPS
    "django.contrib.admin",                  # Admin panel
    "django.contrib.auth",                   # Authentication system
    "django.contrib.contenttypes",           # Content type framework
    "django.contrib.sessions",               # Session framework
    "django.contrib.messages",               # Messaging framework
    "django.contrib.staticfiles",            # Static file handling
]
"""
INSTALLED_APPS: List of all apps that Django should know about

WHY ORDER MATTERS:
- Your apps should come FIRST
- This ensures your templates/static files override defaults
- Third-party apps before Django built-ins

WHAT EACH APP DOES:
-------------------
fundraisers.apps.FundraisersConfig:
    Your main app with Fundraiser and Pledge models

users.apps.UsersConfig:
    Your custom user app with CustomUser model

rest_framework:
    Django REST Framework - makes building APIs easy
    Provides: Serializers, Views, Authentication, Permissions

rest_framework.authtoken:
    Adds Token model for token-based authentication
    Users get a token after login to use in API requests

corsheaders:
    Adds CORS headers to responses
    Allows your frontend (on different domain) to call the API

django.contrib.admin:
    The Django admin panel at /admin/
    Auto-generates CRUD interfaces for your models

django.contrib.auth:
    User authentication (login, logout, passwords)
    Provides the User model we extended with CustomUser

django.contrib.contenttypes:
    Tracks all models in your project
    Used by other apps for generic relations

django.contrib.sessions:
    Server-side session storage
    Enables "remember me" functionality

django.contrib.messages:
    Flash messages ("Profile updated successfully!")
    Shows one-time messages to users

django.contrib.staticfiles:
    Collects and serves static files (CSS, JS, images)
"""


# =============================================================================
# REST FRAMEWORK SETTINGS
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}
"""
REST FRAMEWORK CONFIGURATION

DEFAULT_AUTHENTICATION_CLASSES:
How users prove their identity when making API requests.

TokenAuthentication:
- User logs in and gets a token
- Token is sent with each request: Authorization: Token abc123...
- Server validates the token and identifies the user

OTHER OPTIONS:
- SessionAuthentication: Uses Django sessions (browser cookies)
- BasicAuthentication: Username/password with each request (not secure!)
- JWTAuthentication: JSON Web Tokens (requires extra package)

You can use multiple:
'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework.authentication.TokenAuthentication',
    'rest_framework.authentication.SessionAuthentication',
]
"""


# =============================================================================
# CUSTOM USER MODEL
# =============================================================================

AUTH_USER_MODEL = 'users.CustomUser'
"""
AUTH_USER_MODEL: Tells Django to use your custom user model

FORMAT: 'app_name.ModelName'

IMPORTANT:
- Set this BEFORE running your first migration!
- Changing this after migrations exist is complicated

WHY USE A CUSTOM USER MODEL?
- Add extra fields (profile picture, bio, etc.)
- Change authentication (email instead of username)
- Future-proof your project

EVERYWHERE Django expects a user model, it will now use CustomUser:
- request.user
- ForeignKey to user
- Admin panel
- Authentication
"""


# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",      # Security headers
    "whitenoise.middleware.WhiteNoiseMiddleware",         # Serve static files
    "corsheaders.middleware.CorsMiddleware",              # CORS headers
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",          # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
"""
MIDDLEWARE: Functions that process EVERY request/response

Think of middleware as a pipeline:
    Request → [Middleware 1] → [Middleware 2] → ... → View
    Response ← [Middleware 1] ← [Middleware 2] ← ... ← View

Each middleware can:
- Modify the request before it reaches the view
- Modify the response before it reaches the user
- Block requests entirely (authentication, rate limiting)

ORDER MATTERS! Middleware runs top-to-bottom for requests,
bottom-to-top for responses.

KEY MIDDLEWARE EXPLAINED:
-------------------------
SecurityMiddleware:
    Adds security headers (HTTPS redirect, XSS protection)

WhiteNoiseMiddleware:
    Serves static files in production without nginx
    Must be near the top!

CorsMiddleware:
    Adds CORS headers to allow cross-origin requests
    Must be before CommonMiddleware

SessionMiddleware:
    Manages session data for users

CommonMiddleware:
    URL normalization, content-length headers

CsrfViewMiddleware:
    Protects against Cross-Site Request Forgery attacks
    (Not used for API tokens, but important for forms)

AuthenticationMiddleware:
    Adds request.user to every request

MessageMiddleware:
    Enables flash messages

XFrameOptionsMiddleware:
    Prevents your site from being embedded in iframes (clickjacking)
"""


# =============================================================================
# URL CONFIGURATION
# =============================================================================

ROOT_URLCONF = "crowdfunding.urls"
"""
ROOT_URLCONF: The main URL configuration file

When a request comes in, Django looks at this file to start
matching URL patterns. It's the "entry point" for routing.

Points to: crowdfunding/urls.py
"""


# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
"""
TEMPLATES: Configuration for Django's template engine

WHAT ARE TEMPLATES?
HTML files with special Django tags like {{ variable }} and {% if %}

Since you're building an API (not a website with HTML pages),
you mostly won't use templates. But Django admin uses them!

APP_DIRS = True:
Django automatically looks for templates in each app's templates/ folder

CONTEXT_PROCESSORS:
Functions that add variables to every template automatically
(request, user, messages, etc.)
"""


# =============================================================================
# WSGI APPLICATION
# =============================================================================

WSGI_APPLICATION = "crowdfunding.wsgi.application"
"""
WSGI_APPLICATION: The entry point for WSGI servers

WSGI (Web Server Gateway Interface) is how Python web apps
communicate with web servers.

In production, a WSGI server (like Gunicorn) uses this to
run your Django application.

Points to: crowdfunding/wsgi.py
"""


# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
"""
DATABASE CONFIGURATION

This sets up SQLite as the default database.

SQLITE:
- File-based database (db.sqlite3 file)
- Great for development and small projects
- No server needed!
- Limited concurrent writes

DATABASE SETTINGS EXPLAINED:
- ENGINE: Which database system to use
- NAME: Path to the database file (SQLite) or database name (PostgreSQL)

FOR PRODUCTION (PostgreSQL example):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
"""


db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
"""
PRODUCTION DATABASE OVERRIDE

dj_database_url reads the DATABASE_URL environment variable
and converts it to Django database settings.

DATABASE_URL format:
postgres://USER:PASSWORD@HOST:PORT/DBNAME

Example:
DATABASE_URL=postgres://myuser:secret@db.example.com:5432/myapp

If DATABASE_URL is not set, the SQLite configuration above is used.

conn_max_age=500:
Keep database connections open for 500 seconds (performance optimization)
"""


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
"""
PASSWORD VALIDATORS: Rules for password strength

When users create or change passwords, Django checks against these rules.

UserAttributeSimilarityValidator:
    Password can't be too similar to username, email, etc.

MinimumLengthValidator:
    Password must be at least 8 characters (default)

CommonPasswordValidator:
    Password can't be in list of 20,000 common passwords
    (like "password", "123456", "qwerty")

NumericPasswordValidator:
    Password can't be entirely numeric

CUSTOMIZING:
{
    "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    "OPTIONS": {
        "min_length": 12,  # Require 12 characters
    }
},
"""


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True
"""
INTERNATIONALIZATION (i18n) SETTINGS

LANGUAGE_CODE:
    Default language for your site
    Examples: "en-us", "en-gb", "fr", "es", "de"

TIME_ZONE:
    Default timezone for your site
    "UTC" is recommended for servers (convert to user's timezone in frontend)
    Examples: "America/New_York", "Europe/London", "Australia/Sydney"

USE_I18N:
    Enable translation system
    Allows {{ _("Hello") }} to show different languages

USE_TZ:
    Store datetimes in UTC in the database
    Convert to local time when displaying
    ALWAYS keep this True to avoid timezone bugs!
"""


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
"""
STATIC FILES: CSS, JavaScript, Images

STATIC_URL:
    The URL path where static files are served
    Example: /static/css/style.css

STATIC_ROOT:
    Where collectstatic gathers all static files for production
    Run: python manage.py collectstatic
    
    This collects static files from:
    - Each app's static/ folder
    - Third-party packages (like admin, rest_framework)
    
    Into a single staticfiles/ folder for your web server

WhiteNoiseMiddleware then serves these files in production.
"""


# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
"""
DEFAULT PRIMARY KEY TYPE

Every model needs a primary key (unique identifier).
If you don't specify one, Django creates an 'id' field automatically.

BigAutoField:
    64-bit integer, auto-incrementing
    Range: 1 to 9,223,372,036,854,775,807
    Good for most applications

AutoField:
    32-bit integer (older default)
    Range: 1 to 2,147,483,647
    Might run out for very large tables

This setting applies to all new models unless overridden.
"""
