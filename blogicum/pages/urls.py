from django.urls import path
from django.views.generic.base import TemplateView
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutPage.as_view(), name='about'),
    path('rules/', views.RulesPage.as_view(), name='rules'),
]
