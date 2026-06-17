from django import forms
from django.contrib.auth.models import User

from .models import Complaint, Employee, FAQ, Product, Series, UserRole


def _style(fields, placeholder_map=None):
    """Add Bootstrap classes + placeholders (skips checkboxes)."""
    placeholder_map = placeholder_map or {}
    for name, field in fields.items():
        if isinstance(field.widget, forms.CheckboxInput):
            continue
        css = 'custom-select' if isinstance(field.widget, forms.Select) else 'form-control'
        field.widget.attrs.setdefault('class', css)
        if name in placeholder_map:
            field.widget.attrs.setdefault('placeholder', placeholder_map[name])


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields, {'name': 'Enter Series Name'})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'series']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['series'].empty_label = 'Select Product Series'
        _style(self.fields, {'name': 'Enter Product Name'})


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ['name', 'can_add', 'can_edit', 'can_delete', 'can_view']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields, {'name': 'Enter Role Name'})


class EmployeeForm(forms.ModelForm):
    """Add/Edit Employee — also creates/updates the underlying login User."""
    employee_name = forms.CharField(label='Employee Name', max_length=150)
    username = forms.CharField(label='Username', max_length=150, help_text='Used to log in')
    email = forms.EmailField(label='Official Email ID', help_text='Used for password reset')
    password = forms.CharField(
        label='Password', required=False, widget=forms.PasswordInput(render_value=False),
        help_text='On add: leave blank for default "Newline@123". On edit: leave blank to keep current.')

    class Meta:
        model = Employee
        fields = ['user_type', 'region', 'contact_no', 'role', 'is_active']

    field_order = ['employee_name', 'username', 'user_type', 'region', 'contact_no',
                   'email', 'role', 'password', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].empty_label = 'Select User Role'
        self.fields['region'].widget.choices = [('', 'Select Region')] + list(self.fields['region'].choices)[1:]
        _style(self.fields, {
            'employee_name': 'Enter Employee Name',
            'username': 'Login username',
            'contact_no': 'Enter Mobile No',
            'email': 'Enter Official Email ID',
            'password': 'Set / reset password',
        })

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk and self.instance.user_id:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError('That username is already taken.')
        return username


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'registration_date', 'product', 'serial_number', 'customer_name', 'customer_mobile', 'customer_email',
            'complaint_type', 'spoc', 'distributor_partner', 'distributor_mobile',
            'region', 'state', 'district', 'pincode', 'country', 'call',
            'status', 'description',
        ]
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, spoc_region=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].empty_label = 'Select Product'
        self.fields['spoc'].empty_label = 'Select SPOC'
        # SPOC dropdown shows only members of the relevant region (region-locked users)
        if spoc_region:
            self.fields['spoc'].queryset = Employee.objects.select_related('user').filter(region=spoc_region)
        else:
            self.fields['spoc'].queryset = Employee.objects.select_related('user').all()
        _style(self.fields, {
            'serial_number': 'Enter Serial Number',
            'customer_name': 'Enter Customer Name',
            'customer_mobile': 'Enter Contact Number',
            'customer_email': 'Enter Email',
            'complaint_type': 'Enter Complaint Type',
            'distributor_partner': 'Enter Distributor / Partner',
            'distributor_mobile': 'Enter Distributor Mobile',
            'state': 'Enter State',
            'district': 'Enter District',
            'pincode': 'Enter Pincode',
            'country': 'Enter Country',
            'call': 'Call',
        })


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']
        widgets = {'answer': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields, {
            'question': 'Enter the question',
            'answer': 'Enter the answer',
        })
