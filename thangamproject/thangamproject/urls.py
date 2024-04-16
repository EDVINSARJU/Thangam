from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userapp.urls')),
    # Add other project-level URLs here
    
]





# from django.urls import path, include

# urlpatterns = [
#     path('api/', include('thangamproject.urls')),
#     # Add more URL patterns as needed
# ]
