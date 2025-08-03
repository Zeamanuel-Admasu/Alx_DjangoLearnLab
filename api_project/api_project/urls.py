from django.contrib import admin
from django.urls import path, include  # <== make sure include is here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # <== this line is required here
]
