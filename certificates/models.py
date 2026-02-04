# Create your models here.
from django.db import models

class Certificate(models.Model):
    # We use a Choice field to distinguish the record type
    CERT_TYPE_CHOICES = [
        ('BAPTISM', 'Baptism'),
        ('DEDICATION', 'Child Dedication'),
    ]

    # Personal Information
    full_name = models.CharField(max_length=255, help_text="Name of the person on the certificate")
    parent_guardian = models.CharField(max_length=255, blank=True, null=True, help_text="Required for child dedications")
    
    # Contact Information
    phone_number = models.CharField(max_length=20, help_text="Format: +2547XXXXXXXX")
    email = models.EmailField(blank=True, null=True)

    # Event Details
    certificate_type = models.CharField(max_length=20, choices=CERT_TYPE_CHOICES)
    ceremony_date = models.DateField()
    
    # Tracking Status
    is_picked_up = models.BooleanField(default=False, verbose_name="Has been picked up?")
    date_added = models.DateTimeField(auto_now_add=True)
    
    # Reminder Metadata (To help the system track when to send the next alert)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-ceremony_date']

    def __str__(self):
        return f"{self.full_name} - {self.get_certificate_type_display()}"