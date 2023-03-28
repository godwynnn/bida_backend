from django.urls import path,re_path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns=[
   path('register',RegistrationView.as_view(),name='register'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   path('login',LoginView.as_view(),name='login'),
   path('logout',LogoutView.as_view(),name='logout'),


   path('password/change',ChangePassWordView.as_view(),name='password_change'),
   path('password/change/request',RequestPasswordResetView.as_view(),name='request_password_change'),

   path('password/change/verify',VerifyPasswordResetVerify.as_view(),name='verify_password_change'),

   # path('api/register-by-access-token/social/<str:backend>/', register_by_access_token),
   re_path('api/register-by-access-token/' + r'social/(?P<backend>[^/]+)/$', register_by_access_token),

    
]