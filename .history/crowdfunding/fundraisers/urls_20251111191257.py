from django.urls import path
from . import views

urlpatterns = [
    path('fundraisers/', views.FundraiserList.as_view()),
]