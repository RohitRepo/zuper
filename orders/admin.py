from django.contrib import admin
from .models import Order

import unicodecsv
from django.http import HttpResponse

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

class OrderAdmin(admin.ModelAdmin):
	list_display = ('description', 'status', "customer", "order_type")
	list_filter = (
		('status'),
		("order_type")
	)
	actions = [export_as_csv_action("CSV Export", fields=['description','status'])]

admin.site.register(Order, OrderAdmin)