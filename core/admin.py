from django.contrib import admin

from .models import Complaint, Employee, FAQ, Product, Series, UserRole


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'role', 'region', 'contact_no', 'is_active')
    list_filter = ('user_type', 'region', 'is_active')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('ticket_no', 'product', 'customer_name', 'region', 'status',
                    'registration_date', 'closed_date', 'days_open')
    list_filter = ('status', 'region')
    search_fields = ('ticket_no', 'customer_name')


admin.site.register(Series)
admin.site.register(Product)
admin.site.register(UserRole)
admin.site.register(FAQ)
