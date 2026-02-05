# church_clerk/urls.py
from django.contrib import admin
from django.urls import path
from portal.views import home, reports_view, download_pdf_report

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('reports/', reports_view, name='reports'),
    path('reports/pdf/', download_pdf_report, name='download_pdf'),
]