import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (ComplaintForm, EmployeeForm, FAQForm, ProductForm,
                    SeriesForm, UserRoleForm)
from .models import (Complaint, Employee, FAQ, Product, RESOLVED_STATUSES,
                     Series, UserRole)

# Super admins (and MD) see every region; everyone else is region-locked.
SUPER_TYPES = {'Super Admin', 'MD'}
PRIVILEGED = {'Super Admin', 'Admin', 'MD'}


def _is_super(user):
    if user.is_superuser:
        return True
    emp = getattr(user, 'employee', None)
    return bool(emp and emp.user_type in SUPER_TYPES)


def _is_privileged(user):
    if user.is_superuser:
        return True
    emp = getattr(user, 'employee', None)
    return bool(emp and emp.user_type in PRIVILEGED)


def _user_region(user):
    emp = getattr(user, 'employee', None)
    return emp.region if emp else ''


def scope_complaints(user):
    """All complaints for super admins; only the user's region for normal admins."""
    qs = Complaint.objects.select_related('product', 'spoc__user')
    if _is_super(user):
        return qs
    region = _user_region(user)
    if region:
        return qs.filter(region=region)
    return qs.filter(created_by=user)   # no region assigned -> only own


# super-admin-only views (user/role/series/product management)
super_admin_required = user_passes_test(_is_super, login_url='dashboard')
# super admin + regional admin (not employees) — e.g. Reports
privileged_required = user_passes_test(_is_privileged, login_url='dashboard')


# ---------------------------------------------------------------- Dashboard
@login_required
def dashboard(request):
    qs = scope_complaints(request.user)   # region-locked for normal admins

    # optional date filter (From / To on registration_date)
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    if date_from:
        qs = qs.filter(registration_date__gte=date_from)
    if date_to:
        qs = qs.filter(registration_date__lte=date_to)

    product_data = list(qs.values('product__name').annotate(c=Count('id')).order_by('-c'))
    region_data = list(qs.values('region').annotate(c=Count('id')).order_by('-c'))

    resolved_qs = qs.filter(status__in=RESOLVED_STATUSES)
    open_qs = qs.exclude(status__in=RESOLVED_STATUSES)

    resolved_list = list(resolved_qs)
    avg_days = round(sum(c.days_open for c in resolved_list) / len(resolved_list), 1) if resolved_list else 0

    open_count = open_qs.count()
    overdue_count = sum(1 for c in open_qs if c.days_open > 7)

    context = {
        'active_menu': 'dashboard',
        'total': qs.count(),
        'open_count': open_count,
        'pending_count': open_count,
        'resolved_count': resolved_qs.count(),
        'overdue_count': overdue_count,
        'ontrack_count': open_count - overdue_count,
        'avg_days': avg_days,
        'product_labels': json.dumps([p['product__name'] or 'Unknown' for p in product_data]),
        'product_values': json.dumps([p['c'] for p in product_data]),
        'region_labels': json.dumps([r['region'] or 'Unknown' for r in region_data]),
        'region_values': json.dumps([r['c'] for r in region_data]),
        'complaints': qs.order_by('-id')[:300],   # cap for dashboard render; full list on Complaint page
        'date_from': date_from or '',
        'date_to': date_to or '',
        'region_locked': (not _is_super(request.user)) and _user_region(request.user),
    }
    return render(request, 'core/dashboard.html', context)


# ---------------------------------------------------------------- Series
@super_admin_required
def series_add(request):
    form = SeriesForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Series added successfully.')
        return redirect('series_list')
    return render(request, 'core/series_form.html', {'form': form, 'active_menu': 'series'})


@super_admin_required
def series_edit(request, pk):
    obj = get_object_or_404(Series, pk=pk)
    form = SeriesForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Series updated successfully.')
        return redirect('series_list')
    return render(request, 'core/series_form.html', {'form': form, 'active_menu': 'series', 'editing': obj})


@super_admin_required
def series_list(request):
    return render(request, 'core/series_list.html',
                  {'rows': Series.objects.all(), 'active_menu': 'series'})


@super_admin_required
def series_delete(request, pk):
    get_object_or_404(Series, pk=pk).delete()
    messages.success(request, 'Series deleted.')
    return redirect('series_list')


# ---------------------------------------------------------------- Product
@super_admin_required
def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully.')
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'active_menu': 'product'})


@super_admin_required
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'active_menu': 'product', 'editing': obj})


@super_admin_required
def product_list(request):
    return render(request, 'core/product_list.html',
                  {'rows': Product.objects.select_related('series').all(), 'active_menu': 'product'})


@super_admin_required
def product_delete(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, 'Product deleted.')
    return redirect('product_list')


# ---------------------------------------------------------------- User Roles
@super_admin_required
def role_add(request):
    form = UserRoleForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Role added successfully.')
        return redirect('role_list')
    return render(request, 'core/role_form.html', {'form': form, 'active_menu': 'user_roles'})


@super_admin_required
def role_edit(request, pk):
    obj = get_object_or_404(UserRole, pk=pk)
    form = UserRoleForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Role updated successfully.')
        return redirect('role_list')
    return render(request, 'core/role_form.html', {'form': form, 'active_menu': 'user_roles', 'editing': obj})


@super_admin_required
def role_list(request):
    return render(request, 'core/role_list.html',
                  {'rows': UserRole.objects.all(), 'active_menu': 'user_roles'})


@super_admin_required
def role_delete(request, pk):
    get_object_or_404(UserRole, pk=pk).delete()
    messages.success(request, 'Role deleted.')
    return redirect('role_list')


# ---------------------------------------------------------------- Employees / Users
@super_admin_required
def employee_add(request):
    form = EmployeeForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['employee_name']
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data.get('password') or 'Newline@123'
        parts = name.split(' ', 1)
        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=parts[0], last_name=parts[1] if len(parts) > 1 else '',
        )
        emp = form.save(commit=False)
        emp.user = user
        emp.save()
        user.is_active = emp.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, f'Employee "{name}" added. They can log in with username "{username}".')
        return redirect('employee_list')
    return render(request, 'core/employee_form.html', {'form': form, 'active_menu': 'users'})


@super_admin_required
def employee_toggle(request, pk):
    """Activate / deactivate a user account."""
    emp = get_object_or_404(Employee, pk=pk)
    emp.is_active = not emp.is_active
    emp.save(update_fields=['is_active'])
    if emp.user:
        emp.user.is_active = emp.is_active
        emp.user.save(update_fields=['is_active'])
    messages.success(request, f'{emp} is now {"Active" if emp.is_active else "Inactive"}.')
    return redirect('employee_list')


@super_admin_required
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    initial = {'employee_name': emp.user.get_full_name() or emp.user.username,
               'username': emp.user.username, 'email': emp.user.email}
    form = EmployeeForm(request.POST or None, instance=emp, initial=initial)
    if form.is_valid():
        emp = form.save()
        # keep the linked login user in sync
        name = form.cleaned_data['employee_name']
        parts = name.split(' ', 1)
        u = emp.user
        u.first_name = parts[0]
        u.last_name = parts[1] if len(parts) > 1 else ''
        u.username = form.cleaned_data['username']
        u.email = form.cleaned_data['email']
        if form.cleaned_data.get('password'):
            u.set_password(form.cleaned_data['password'])   # super admin can reset any password
        u.is_active = emp.is_active
        u.save()
        messages.success(request, f'Employee "{name}" updated.')
        return redirect('employee_list')
    return render(request, 'core/employee_form.html', {'form': form, 'active_menu': 'users', 'editing': emp})


@super_admin_required
def employee_list(request):
    rows = Employee.objects.select_related('user', 'role').all()
    region = request.GET.get('region')
    user_type = request.GET.get('user_type')
    if region and region != 'All':
        rows = rows.filter(region=region)
    if user_type:
        rows = rows.filter(user_type=user_type)
    return render(request, 'core/employee_list.html', {
        'rows': rows,
        'active_menu': 'users',
        'regions': [c[0] for c in Employee._meta.get_field('region').choices],
        'user_types': [c[0] for c in Employee.USER_TYPE_CHOICES],
    })


@super_admin_required
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if emp.user:
        emp.user.delete()  # cascades to employee
    else:
        emp.delete()
    messages.success(request, 'Employee removed.')
    return redirect('employee_list')


# ---------------------------------------------------------------- Complaints
@login_required
def complaint_add(request):
    spoc_region = None if _is_super(request.user) else _user_region(request.user)
    form = ComplaintForm(request.POST or None, spoc_region=spoc_region)
    if form.is_valid():
        complaint = form.save(commit=False)
        complaint.created_by = request.user
        if not _is_super(request.user) and _user_region(request.user):
            complaint.region = _user_region(request.user)   # lock to own region
        complaint.save()
        messages.success(request, f'Complaint {complaint.ticket_no} registered.')
        return redirect('complaint_list')
    return render(request, 'core/complaint_form.html', {'form': form, 'active_menu': 'complaint'})


@login_required
def complaint_list(request):
    rows = scope_complaints(request.user)   # region-locked for normal admins

    product = request.GET.get('product')
    region = request.GET.get('region')
    status = request.GET.get('status')
    if product and product != 'All':
        rows = rows.filter(product_id=product)
    if region and region != 'All':
        rows = rows.filter(region=region)
    if status and status != 'All':
        rows = rows.filter(status=status)
    rows = rows.order_by('-id')

    return render(request, 'core/complaint_list.html', {
        'rows': rows,
        'total_count': rows.count(),
        'active_menu': 'complaint',
        'products': Product.objects.all(),
        'regions': [c[0] for c in Complaint._meta.get_field('region').choices],
        'statuses': [c[0] for c in Complaint.STATUS_CHOICES],
        'region_locked': (not _is_super(request.user)) and _user_region(request.user),
    })


@login_required
def complaint_detail(request, pk):
    # scoped: region-locked users can only view their region's complaints
    complaint = get_object_or_404(scope_complaints(request.user), pk=pk)
    return render(request, 'core/complaint_detail.html', {'c': complaint, 'active_menu': 'complaint'})


@login_required
def complaint_edit(request, pk):
    # scoped: a regional admin/employee can only open complaints in their region
    complaint = get_object_or_404(scope_complaints(request.user), pk=pk)
    spoc_region = None if _is_super(request.user) else _user_region(request.user)
    form = ComplaintForm(request.POST or None, instance=complaint, spoc_region=spoc_region)
    if form.is_valid():
        obj = form.save(commit=False)
        if not _is_super(request.user) and _user_region(request.user):
            obj.region = _user_region(request.user)
        obj.save()
        messages.success(request, f'Complaint {complaint.ticket_no} updated.')
        return redirect('complaint_list')
    return render(request, 'core/complaint_form.html',
                  {'form': form, 'active_menu': 'complaint', 'editing': complaint})


@super_admin_required
def complaint_delete(request, pk):
    get_object_or_404(Complaint, pk=pk).delete()
    messages.success(request, 'Complaint deleted.')
    return redirect('complaint_list')


# ---------------------------------------------------------------- FAQ
@login_required
def faq_add(request):
    form = FAQForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'FAQ added successfully.')
        return redirect('faq_list')
    return render(request, 'core/faq_form.html', {'form': form, 'active_menu': 'faq'})


@login_required
def faq_edit(request, pk):
    obj = get_object_or_404(FAQ, pk=pk)
    form = FAQForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'FAQ updated successfully.')
        return redirect('faq_list')
    return render(request, 'core/faq_form.html', {'form': form, 'active_menu': 'faq', 'editing': obj})


@login_required
def faq_list(request):
    return render(request, 'core/faq_list.html',
                  {'rows': FAQ.objects.all(), 'active_menu': 'faq'})


@login_required
def faq_delete(request, pk):
    get_object_or_404(FAQ, pk=pk).delete()
    messages.success(request, 'FAQ deleted.')
    return redirect('faq_list')


# ---------------------------------------------------------------- Reports
@privileged_required
def reports(request):
    """Per-employee call record: total calls, abort, avg days, pending + day buckets.
    Super admin sees all regions; normal admin only their region."""
    all_c = list(scope_complaints(request.user))

    # group by SPOC employee
    rows = {}
    for c in all_c:
        emp = c.spoc
        key = emp.id if emp else 0
        if key not in rows:
            rows[key] = {
                'region': (emp.region if emp else c.region) or '-',
                'emp': str(emp) if emp else 'Unassigned',
                'total': 0, 'abort': 0, 'pending': 0,
                'resolved_days': [], 'b27': 0, 'b715': 0, 'b1530': 0,
            }
        r = rows[key]
        r['total'] += 1
        if c.status == 'Abort':
            r['abort'] += 1
        if c.is_resolved:
            r['resolved_days'].append(c.days_open)
        else:
            r['pending'] += 1
            d = c.days_open                      # pending-call day buckets
            if 2 < d <= 7:
                r['b27'] += 1
            elif 7 < d <= 15:
                r['b715'] += 1
            elif 15 < d <= 30:
                r['b1530'] += 1

    report_rows = []
    for r in rows.values():
        avg = round(sum(r['resolved_days']) / len(r['resolved_days']), 1) if r['resolved_days'] else 0
        report_rows.append({
            'region': r['region'], 'emp': r['emp'], 'total': r['total'],
            'abort': r['abort'], 'avg': avg, 'pending': r['pending'],
            'b27': r['b27'], 'b715': r['b715'], 'b1530': r['b1530'],
        })
    report_rows.sort(key=lambda x: (x['region'], x['emp']))

    return render(request, 'core/reports.html', {
        'active_menu': 'reports',
        'report_rows': report_rows,
        'region_locked': (not _is_super(request.user)) and _user_region(request.user),
    })


# ---------------------------------------------------------------- Change password
@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)   # stay logged in
        messages.success(request, 'Your password was changed successfully.')
        return redirect('dashboard')
    return render(request, 'core/change_password.html', {'form': form, 'active_menu': ''})
