from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', signupView.as_view(), name='signup'),
    path('login/', loginView.as_view(), name='login'),
    path('logout/', logoutView, name='logout'),
    path('profile/', user_profile.as_view(), name='profile'),
    path('update-profile-picture/', update_profile_picture, name='update_profile_picture'),
]