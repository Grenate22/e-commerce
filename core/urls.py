from django.views.generic import TemplateView
from django.urls import path

urlpatterns = [
    path('index/', TemplateView.as_view(template_name='core/index.html'))
]
