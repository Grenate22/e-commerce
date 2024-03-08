

from rest_framework import permissions 
from drf_yasg.views import get_schema_view 
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from drf_yasg import openapi 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path




schema_view = get_schema_view( 
   openapi.Info( 
      title="Grenate Api", 
      default_version='v1', 
      description="Dummy description", 
      terms_of_service="https://www.google.com/policies/terms/", 
      contact=openapi.Contact(email="peteradetunji30@gmail.com"), 
      license=openapi.License(name="BSD License"), 
   ), 
   public=True, 
   permission_classes=(permissions.AllowAny,), 
) 

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   #  path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('user/',include('core.urls')),
    path('admin/', admin.site.urls),
    path('',include('playground.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
    path('store/', include('storre.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
    
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
