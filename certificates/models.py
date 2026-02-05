from django.db import models

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