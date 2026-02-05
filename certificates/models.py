from time import timezone
from django.db import models
from django.utils import timezone as django_timezone    

class Certificate(models.Model):
    CERT_TYPES = [('BAPTISM', 'Baptism'), ('DEDICATION', 'Child Dedication')]

    # Common Fields
    full_name = models.CharField(max_length=255, verbose_name="Name")
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    ceremony_date = models.DateField()
    is_picked_up = models.BooleanField(default=False)
    
    # Specific Fields
    certificate_type = models.CharField(max_length=20, choices=CERT_TYPES)
    parent_guardian = models.CharField(max_length=255, blank=True, null=True)
    officiating_pastor = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.certificate_type})"

# Proxy Models to separate them in the Sidebar
class Baptism(Certificate):
    class Meta:
        proxy = True
        verbose_name = "Baptism Certificate"
        verbose_name_plural = "Baptism Certificates"

class Dedication(Certificate):
    class Meta:
        proxy = True
        verbose_name = "Child Dedication"
        verbose_name_plural = "Child Dedications"


class HolyCommunion(models.Model):
    date = models.DateField()
    participants_count = models.PositiveIntegerField(verbose_name="Total Participants")
    # This stores the image file in a folder called 'communion_sheets'
    sheet_image = models.ImageField(upload_to='communion_sheets/', help_text="Upload a photo of the attendance sheet")

    class Meta:
        verbose_name = "Holy Communion Record"
        ordering = ['-date']

    def __str__(self):
        return f"Communion on {self.date}"
    

class MemberTransfer(models.Model):
    TRANSFER_TYPES = (
        ('IN', 'Incoming'),
        ('OUT', 'Outgoing'),
    )
    
    STAGES = (
        ('PR', 'Processing'),
        ('R1', 'First Reading'),
        ('R2', 'Second Reading'),
        ('MB', 'Member (Finalized)'),
    )

    full_name = models.CharField(max_length=200)
    transfer_type = models.CharField(max_length=3, choices=TRANSFER_TYPES, default='IN')
    church_involved = models.CharField(max_length=255, help_text="SDA Church transferring to/from")
    stage = models.CharField(max_length=2, choices=STAGES, default='PR')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    date_started = models.DateField(auto_now_add=True)
    
    date_completed = models.DateField(null=True, blank=True, editable=False) 
    last_updated = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        
        if self.stage == 'MB' and not self.date_completed:
            
            self.date_completed = django_timezone.now().date()
        
        elif self.stage != 'MB':
            self.date_completed = None
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Membership Transfer"
        ordering = ['-last_updated']

    def __str__(self):
        return f"{self.full_name} - {self.get_transfer_type_display()}"