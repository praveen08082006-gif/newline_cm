from django import forms

from .models import Complaint, Employee, FAQ, Product, Series, UserRole


def _style(fields, placeholder_map=None):
    """Add Bootstrap classes + placeholders to a set of form fields."""
    placeholder_map = placeholder_map or {}
    for name, field in fields.items():
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
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self.fields, {'name': 'Enter Role Name'})


class EmployeeForm(forms.ModelForm):
    """Add Employee form — also creates the underlying login User."""
    employee_name = forms.CharField(label='Employee Name', max_length=150)
    email = forms.EmailField(label='Official Email ID')

    class Meta:
        model = Employee
        fields = ['user_type', 'region', 'contact_no', 'role']

    field_order = ['employee_name', 'user_type', 'region', 'contact_no', 'email', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].empty_label = 'Select User Role'
        self.fields['region'].widget.choices = [('', 'Select Region')] + list(self.fields['region'].choices)[1:]
        _style(self.fields, {
            'employee_name': 'Enter Employee Name',
            'contact_no': 'Enter Mobile No',
            'email': 'Enter Official Email ID',
        })


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'product', 'customer_name', 'customer_mobile',
            'spoc', 'distributor_partner', 'distributor_mobile',
            'region', 'status', 'registration_date', 'description',
        ]
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].empty_label = 'Select Product'
        self.fields['spoc'].empty_label = 'Select SPOC'
        _style(self.fields, {
            'customer_name': 'Enter Customer Name',
            'customer_mobile': 'Enter Customer Mobile',
            'distributor_partner': 'Enter Distributor / Partner',
            'distributor_mobile': 'Enter Distributor Mobile',
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
