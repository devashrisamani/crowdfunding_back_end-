from django.urls import path
from . import views


urlpatterns = [
    path('fundraisers/', views.FundraiserList.as_view()),
    path('fundraisers/<int:pk>/', views.FundraiserDetail.as_view()),    
    path('pledges/', views.PledgeList.as_view()),    
    path('pledges/<int:pk>/', views.PledgeDetail.as_view()),
    path('me/fundraisers/', views.MyFundraisers.as_view()),
    path('me/pledges/', views.MyPledges.as_view()),
        path("users/me/", views.CurrentUser.as_view()),

]
