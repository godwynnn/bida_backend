
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('appauth.urls')),
    path('events/',include('events.urls')),
]

# urlpatterns+=static()