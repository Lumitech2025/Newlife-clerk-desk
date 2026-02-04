from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'certificate_type', 'ceremony_date', 'phone_number', 'is_picked_up')
    list_filter = ('certificate_type', 'is_picked_up', 'ceremony_date')
    search_fields = ('full_name', 'phone_number')
    actions = ['mark_as_picked_up']

    def mark_as_picked_up(self, request, queryset):
        queryset.update(is_picked_up=True)
    mark_as_picked_up.short_description = "Mark selected certificates as Picked Up"
