# portal/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from certificates.models import Baptism, Dedication
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import datetime

def home(request):
    return render(request, 'portal/index.html')

@login_required
def reports_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    baptism_qs = Baptism.objects.all()
    dedication_qs = Dedication.objects.all()

    if start_date and end_date:
        baptism_qs = baptism_qs.filter(ceremony_date__range=[start_date, end_date])
        dedication_qs = dedication_qs.filter(ceremony_date__range=[start_date, end_date])

    # Aggregating data by month number
    b_raw = baptism_qs.annotate(month=ExtractMonth('ceremony_date'))\
        .values('month').annotate(total=Count('id')).order_by('month')
    
    d_raw = dedication_qs.annotate(month=ExtractMonth('ceremony_date'))\
        .values('month').annotate(total=Count('id')).order_by('month')

    # Month name mapping
    month_map = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    # Formatting for the table: January: 5, etc.
    baptism_stats = [{'month_name': month_map[item['month']], 'total': item['total']} for item in b_raw]
    dedication_stats = [{'month_name': month_map[item['month']], 'total': item['total']} for item in d_raw]

    context = {
        'baptism_stats': baptism_stats,
        'dedication_stats': dedication_stats,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'portal/reports.html', context)

@login_required
def download_pdf_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    b_qs = Baptism.objects.all()
    d_qs = Dedication.objects.all()

    if start_date and end_date:
        b_qs = b_qs.filter(ceremony_date__range=[start_date, end_date])
        d_qs = d_qs.filter(ceremony_date__range=[start_date, end_date])

    response = HttpResponse(content_type='application/pdf')
    filename = f"Newlife_Report_{start_date}_to_{end_date}.pdf" if start_date else "Full_Report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=letter)
    
    # PDF Header
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(300, 750, "NEWLIFE SDA CHURCH")
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(300, 730, "CLERK'S MINISTRY REPORT")
    
    p.setFont("Helvetica", 10)
    period = f"{start_date} to {end_date}" if start_date else "All Time"
    p.drawString(70, 700, f"Report Period: {period}")
    p.drawString(70, 685, f"Generated: {datetime.date.today()}")
    p.line(70, 680, 530, 680)

    # Content
    p.setFont("Helvetica-Bold", 12)
    p.drawString(70, 640, "STATISTICAL SUMMARY")
    p.setFont("Helvetica", 12)
    p.drawString(70, 620, f"• Total Baptisms: {b_qs.count()}")
    p.drawString(70, 600, f"• Total Child Dedications: {d_qs.count()}")
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(70, 550, "Signed: __________________________ (Church Clerk)")

    p.showPage()
    p.save()
    return response