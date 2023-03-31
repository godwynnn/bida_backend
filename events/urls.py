from django.urls import path,include
from .views import *

urlpatterns=[
    path('',EventsView.as_view(),name='events'),
    path('packages',PackagesView.as_view(),name='packages'),
    path('select/package/event',SelectPackageForEvent.as_view(),name='package_event'),
    path('select/package/event/duration',IncreaseDecreaseDurationView.as_view(),name='set_duration'),
    path('select/otp/verification',OTPPaymentVerification.as_view(),name='otp_verification'),
]
