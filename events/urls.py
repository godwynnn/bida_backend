from django.urls import path,include
from .views import *

urlpatterns=[
    path('',EventsView.as_view(),name='events')
]
