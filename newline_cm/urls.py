"""URL configuration for newline_cm project."""
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

    # Forgot / reset password (emailed link)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password-reset/done/'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('change-password/', core_views.change_password, name='change_password'),

    # Users / Employees
    path('employee/add/', core_views.employee_add, name='employee_add'),
    path('employee/', core_views.employee_list, name='employee_list'),
    path('employee/<int:pk>/edit/', core_views.employee_edit, name='employee_edit'),
    path('employee/<int:pk>/toggle/', core_views.employee_toggle, name='employee_toggle'),
    path('employee/<int:pk>/delete/', core_views.employee_delete, name='employee_delete'),

    # User Roles
    path('role/add/', core_views.role_add, name='role_add'),
    path('role/', core_views.role_list, name='role_list'),
    path('role/<int:pk>/edit/', core_views.role_edit, name='role_edit'),
    path('role/<int:pk>/delete/', core_views.role_delete, name='role_delete'),

    # Series
    path('series/add/', core_views.series_add, name='series_add'),
    path('series/', core_views.series_list, name='series_list'),
    path('series/<int:pk>/edit/', core_views.series_edit, name='series_edit'),
    path('series/<int:pk>/delete/', core_views.series_delete, name='series_delete'),

    # Product
    path('product/add/', core_views.product_add, name='product_add'),
    path('product/', core_views.product_list, name='product_list'),
    path('product/<int:pk>/edit/', core_views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', core_views.product_delete, name='product_delete'),

    # Complaint
    path('complaint/add/', core_views.complaint_add, name='complaint_add'),
    path('complaint/', core_views.complaint_list, name='complaint_list'),
    path('complaint/<int:pk>/edit/', core_views.complaint_edit, name='complaint_edit'),
    path('complaint/<int:pk>/delete/', core_views.complaint_delete, name='complaint_delete'),

    # FAQ
    path('faq/add/', core_views.faq_add, name='faq_add'),
    path('faq/', core_views.faq_list, name='faq_list'),
    path('faq/<int:pk>/edit/', core_views.faq_edit, name='faq_edit'),
    path('faq/<int:pk>/delete/', core_views.faq_delete, name='faq_delete'),

    # Reports
    path('reports/', core_views.reports, name='reports'),
]
