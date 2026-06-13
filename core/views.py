import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (ComplaintForm, EmployeeForm, FAQForm, ProductForm,
                    SeriesForm, UserRoleForm)
from .models import Complaint, Employee, FAQ, Product, Series, UserRole

# User types that are allowed to see the whole system (MD sees everything).
PRIVILEGED = {'Super Admin', 'Admin', 'MD'}


def _is_privileged(user):
    if user.is_superuser:
        return True
    emp = getattr(user, 'employee', None)
    return bool(emp and emp.user_type in PRIVILEGED)


# ---------------------------------------------------------------- Dashboard
@login_required
def dashboard(request):
    qs = Complaint.objects.all()

    # optional date filter (From / To on registration_date)
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    if date_from:
        qs = qs.filter(registration_date__gte=date_from)
    if date_to:
        qs = qs.filter(registration_date__lte=date_to)

    # Product-wise (donut) and Region-wise (pie) aggregates
    product_data = list(qs.values('product__name').annotate(c=Count('id')).order_by('-c'))
    region_data = list(qs.values('region').annotate(c=Count('id')).order_by('-c'))

    open_qs = qs.exclude(status__in=['Resolved', 'Closed'])
    resolved_qs = qs.filter(status__in=['Resolved', 'Closed'])

    context = {
        'active_menu': 'dashboard',
        'total': qs.count(),
        'open_count': open_qs.count(),
        'resolved_count': resolved_qs.count(),
        'overdue_count': sum(1 for c in open_qs if c.days_open > 7),
        'product_labels': json.dumps([p['product__name'] or 'Unknown' for p in product_data]),
        'product_values': json.dumps([p['c'] for p in product_data]),
        'region_labels': json.dumps([r['region'] or 'Unknown' for r in region_data]),
        'region_values': json.dumps([r['c'] for r in region_data]),
        'date_from': date_from or '',
        'date_to': date_to or '',
    }
    return render(request, 'core/dashboard.html', context)


# ---------------------------------------------------------------- Series
@login_required
def series_add(request):
    form = SeriesForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Series added successfully.')
        return redirect('series_list')
    return render(request, 'core/series_form.html', {'form': form, 'active_menu': 'series'})


@login_required
def series_edit(request, pk):
    obj = get_object_or_404(Series, pk=pk)
    form = SeriesForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Series updated successfully.')
        return redirect('series_list')
    return render(request, 'core/series_form.html', {'form': form, 'active_menu': 'series', 'editing': obj})


@login_required
def series_list(request):
    return render(request, 'core/series_list.html',
                  {'rows': Series.objects.all(), 'active_menu': 'series'})


@login_required
def series_delete(request, pk):
    get_object_or_404(Series, pk=pk).delete()
    messages.success(request, 'Series deleted.')
    return redirect('series_list')


# ---------------------------------------------------------------- Product
@login_required
def product_add(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully.')
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'active_menu': 'product'})


@login_required
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('product_list')
    return render(request, 'core/product_form.html', {'form': form, 'active_menu': 'product', 'editing': obj})


@login_required
def product_list(request):
    return render(request, 'core/product_list.html',
                  {'rows': Product.objects.select_related('series').all(), 'active_menu': 'product'})


@login_required
def product_delete(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, 'Product deleted.')
    return redirect('product_list')


# ---------------------------------------------------------------- User Roles
@login_required
def role_add(request):
    form = UserRoleForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Role added successfully.')
        return redirect('role_list')
    return render(request, 'core/role_form.html', {'form': form, 'active_menu': 'user_roles'})


@login_required
def role_edit(request, pk):
    obj = get_object_or_404(UserRole, pk=pk)
    form = UserRoleForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Role updated successfully.')
        return redirect('role_list')
    return render(request, 'core/role_form.html', {'form': form, 'active_menu': 'user_roles', 'editing': obj})


@login_required
def role_list(request):
    return render(request, 'core/role_list.html',
                  {'rows': UserRole.objects.all(), 'active_menu': 'user_roles'})


@login_required
def role_delete(request, pk):
    get_object_or_404(UserRole, pk=pk).delete()
    messages.success(request, 'Role deleted.')
    return redirect('role_list')


# ---------------------------------------------------------------- Employees / Users
@login_required
def employee_add(request):
    form = EmployeeForm(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['employee_name']
        email = form.cleaned_data['email']
        # build a login user from the email (username = part before @)
        username = email.split('@')[0]
        base, n = username, 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{n}'
            n += 1
        parts = name.split(' ', 1)
        user = User.objects.create_user(
            username=username, email=email, password='Newline@123',
            first_name=parts[0], last_name=parts[1] if len(parts) > 1 else '',
        )
        emp = form.save(commit=False)
        emp.user = user
        emp.save()
        messages.success(request, f'Employee "{name}" added. Temp password: Newline@123')
        return redirect('employee_list')
    return render(request, 'core/employee_form.html', {'form': form, 'active_menu': 'users'})


@login_required
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    initial = {'employee_name': emp.user.get_full_name() or emp.user.username,
               'email': emp.user.email}
    form = EmployeeForm(request.POST or None, instance=emp, initial=initial)
    if form.is_valid():
        emp = form.save()
        # keep the linked login user's name + email in sync
        name = form.cleaned_data['employee_name']
        parts = name.split(' ', 1)
        emp.user.first_name = parts[0]
        emp.user.last_name = parts[1] if len(parts) > 1 else ''
        emp.user.email = form.cleaned_data['email']
        emp.user.save()
        messages.success(request, f'Employee "{name}" updated.')
        return redirect('employee_list')
    return render(request, 'core/employee_form.html', {'form': form, 'active_menu': 'users', 'editing': emp})


@login_required
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


@login_required
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
    form = ComplaintForm(request.POST or None)
    if form.is_valid():
        complaint = form.save(commit=False)
        complaint.created_by = request.user
        complaint.save()
        messages.success(request, f'Complaint {complaint.ticket_no} registered.')
        return redirect('complaint_list')
    return render(request, 'core/complaint_form.html', {'form': form, 'active_menu': 'complaint'})


@login_required
def complaint_list(request):
    rows = Complaint.objects.select_related('product', 'spoc__user').all()
    # Employees who are NOT privileged only see complaints they created/own
    if not _is_privileged(request.user):
        emp = getattr(request.user, 'employee', None)
        rows = rows.filter(created_by=request.user) if emp is None else \
            rows.filter(spoc=emp) | rows.filter(created_by=request.user)
        rows = rows.distinct()

    product = request.GET.get('product')
    region = request.GET.get('region')
    status = request.GET.get('status')
    if product and product != 'All':
        rows = rows.filter(product_id=product)
    if region and region != 'All':
        rows = rows.filter(region=region)
    if status and status != 'All':
        rows = rows.filter(status=status)

    return render(request, 'core/complaint_list.html', {
        'rows': rows.order_by('-id'),
        'active_menu': 'complaint',
        'products': Product.objects.all(),
        'regions': [c[0] for c in Complaint._meta.get_field('region').choices],
        'statuses': [c[0] for c in Complaint.STATUS_CHOICES],
    })


@login_required
def complaint_edit(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    form = ComplaintForm(request.POST or None, instance=complaint)
    if form.is_valid():
        form.save()
        messages.success(request, f'Complaint {complaint.ticket_no} updated.')
        return redirect('complaint_list')
    return render(request, 'core/complaint_form.html',
                  {'form': form, 'active_menu': 'complaint', 'editing': complaint})


@login_required
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
@login_required
def reports(request):
    """Resolution-time report with day buckets + per-employee performance."""
    resolved = Complaint.objects.filter(status__in=['Resolved', 'Closed'])
    open_complaints = Complaint.objects.exclude(status__in=['Resolved', 'Closed'])

    buckets = {'0-2': 0, '>2<7': 0, '>7<15': 0, '>15<30': 0, '>30': 0}
    for c in resolved:
        d = c.days_open
        if d <= 2:
            buckets['0-2'] += 1
        elif d < 7:
            buckets['>2<7'] += 1
        elif d < 15:
            buckets['>7<15'] += 1
        elif d < 30:
            buckets['>15<30'] += 1
        else:
            buckets['>30'] += 1

    # employee performance: resolved count + average days to close
    perf = []
    for emp in Employee.objects.select_related('user').all():
        emp_resolved = [c for c in resolved if c.spoc_id == emp.id]
        if not emp_resolved:
            continue
        avg_days = round(sum(c.days_open for c in emp_resolved) / len(emp_resolved), 1)
        perf.append({'name': str(emp), 'count': len(emp_resolved), 'avg_days': avg_days})
    perf.sort(key=lambda x: x['avg_days'])

    return render(request, 'core/reports.html', {
        'active_menu': 'reports',
        'buckets': buckets,
        'bucket_labels': json.dumps(list(buckets.keys())),
        'bucket_values': json.dumps(list(buckets.values())),
        'performance': perf,
        'open_overdue': [c for c in open_complaints if c.days_open > 7],
    })
