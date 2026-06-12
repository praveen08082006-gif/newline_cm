"""
URL configuration for newline_cm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('dashboard/', core_views.dashboard, name='dashboard'),
]
