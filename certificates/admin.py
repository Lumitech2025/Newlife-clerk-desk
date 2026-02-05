from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Baptism, Dedication, HolyCommunion, MemberTransfer
from .utils import send_httpsms_reminder, send_church_email

# --- ACTIONS ---

def send_email_reminder(modeladmin, request, queryset):
    success_count = 0
    for record in queryset:
        if record.email:
            # Safely get parent_guardian if it exists (Dedication model), else None (Baptism model)
            parent = getattr(record, 'parent_guardian', None)
            
            status = send_church_email(
                record.email, 
                record.full_name, 
                record.get_certificate_type_display(),
                parent_name=parent # Passing the parent name to utils
            )
            if status:
                success_count += 1
    
    if success_count > 0:
        modeladmin.message_user(request, f"📧 {success_count} emails sent successfully!", messages.SUCCESS)
    else:
        modeladmin.message_user(request, "No emails sent. Ensure records have email addresses.", messages.WARNING)

send_email_reminder.short_description = "📧 Send Email Reminder"

def mark_as_picked_up(modeladmin, request, queryset):
    queryset.update(is_picked_up=True)
mark_as_picked_up.short_description = "✅ Mark as Picked Up"

def send_sms_reminder(modeladmin, request, queryset):
    success_count = 0
    fail_count = 0
    for record in queryset:
        cert_label = record.get_certificate_type_display()
        # Safely get parent_guardian for Dedication records
        parent = getattr(record, 'parent_guardian', None)
        
        status = send_httpsms_reminder(
            record.phone_number, 
            record.full_name, 
            cert_label,
            parent_name=parent # Passing parent name for personalized SMS
        )
        if status:
            success_count += 1
        else:
            fail_count += 1
            
    if success_count > 0:
        modeladmin.message_user(request, f"✅ {success_count} messages queued successfully!", messages.SUCCESS)
    if fail_count > 0:
        modeladmin.message_user(request, f"❌ {fail_count} messages failed. Check the Android phone.", messages.ERROR)

send_sms_reminder.short_description = "📲 Send SMS Reminder"


# --- ADMIN CLASSES ---

@admin.register(Baptism)
class BaptismAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ceremony_date', 'officiating_pastor', 'phone_number', 'status_button')
    fields = ('full_name', 'ceremony_date', 'officiating_pastor', 'location', 'phone_number', 'email', 'is_picked_up')
    actions = [mark_as_picked_up, send_sms_reminder, send_email_reminder] 

    def get_queryset(self, request):
        return super().get_queryset(request).filter(certificate_type='BAPTISM')

    def save_model(self, request, obj, form, change):
        obj.certificate_type = 'BAPTISM'
        super().save_model(request, obj, form, change)

    def status_button(self, obj):
        if obj.is_picked_up:
            return format_html('<span style="padding: 5px 10px; background: #28a745; color: white; border-radius: 4px;">Picked</span>')
        return format_html('<span style="padding: 5px 10px; background: #dc3545; color: white; border-radius: 4px;">Pending</span>')


@admin.register(Dedication)
class DedicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'parent_guardian', 'ceremony_date', 'phone_number', 'status_button')
    fields = ('full_name', 'parent_guardian', 'ceremony_date', 'phone_number', 'email', 'is_picked_up')
    actions = [mark_as_picked_up, send_sms_reminder, send_email_reminder] 

    def get_queryset(self, request):
        return super().get_queryset(request).filter(certificate_type='DEDICATION')

    def save_model(self, request, obj, form, change):
        obj.certificate_type = 'DEDICATION'
        super().save_model(request, obj, form, change)

    def status_button(self, obj):
        if obj.is_picked_up:
            return format_html('<span style="padding: 5px 10px; background: #28a745; color: white; border-radius: 4px;">Picked</span>')
        return format_html('<span style="padding: 5px 10px; background: #dc3545; color: white; border-radius: 4px;">Pending</span>')
    
@admin.register(HolyCommunion)
class HolyCommunionAdmin(admin.ModelAdmin):
    list_display = ('date', 'participants_count', 'sheet_preview')

    fields = ('date', 'participants_count', 'sheet_image')

    def sheet_preview(self, obj):
        if obj.sheet_image:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 4px;" />', obj.sheet_image.url)
        return "No Image"
    
    sheet_preview.short_description = "Sheet Preview"


@admin.register(MemberTransfer)
class MemberTransferAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'transfer_type', 'church_involved', 'stage', 'date_started', 'date_completed')
    list_filter = ('transfer_type', 'stage', 'date_started')
    search_fields = ('full_name', 'church_involved', 'phone_number')
    list_editable = ('stage',)  

    readonly_fields = ('date_started', 'date_completed', 'last_updated')