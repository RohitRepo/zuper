from django import forms
from django.contrib import admin
from .models import User
import unicodecsv
from django.http import HttpResponse
# from django.contrib.auth.forms import UserCreationForm

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone', 'is_superuser', 'is_staff', 'is_active', 'is_online',
         'name', 'email' ,'user_type', 'latitude', 'longitude', 'gcm_token')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        
        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = unicodecsv.writer(response, encoding='utf-8')
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in field_names]
            writer.writerow(row)
        return response
    export_as_csv.short_description = description
    return export_as_csv

class UserAdmin(admin.ModelAdmin):
    form = UserCreationForm

    list_display = ('name', 'phone', "user_type")
    list_filter = (
        ('user_type'),
    )

    search_fields = ('phone', 'name')

    actions = [export_as_csv_action("CSV Export", fields=['name','user_type', 'phone'])]

admin.site.register(User, UserAdmin)