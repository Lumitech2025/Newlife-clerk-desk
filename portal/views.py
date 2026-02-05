# portal/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from certificates.models import Baptism, Dedication, MemberTransfer, HolyCommunion
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import datetime
from django.db.models import Sum

def home(request):
    return render(request, 'portal/index.html')

@login_required
def reports_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 1. Fetch the raw records based on date
    b_qs = Baptism.objects.all()
    d_qs = Dedication.objects.all()

    if start_date and end_date:
        b_qs = b_qs.filter(ceremony_date__range=[start_date, end_date])
        d_qs = d_qs.filter(ceremony_date__range=[start_date, end_date])

    # 2. Manual Python Counting (Prevents SQL Join Multiplications)
    month_map = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    # Initialize empty counters for all 12 months
    b_counts = {i: 0 for i in range(1, 13)}
    d_counts = {i: 0 for i in range(1, 13)}

    # Loop through actual records and increment
    for b in b_qs:
        month = b.ceremony_date.month
        b_counts[month] += 1
    
    for d in d_qs:
        month = d.ceremony_date.month
        d_counts[month] += 1

    # 3. Format only months that have data (> 0)
    baptism_stats = [
        {'month_name': month_map[m], 'total': count} 
        for m, count in b_counts.items() if count > 0
    ]
    
    dedication_stats = [
        {'month_name': month_map[m], 'total': count} 
        for m, count in d_counts.items() if count > 0
    ]

    context = {
        'baptism_stats': baptism_stats,
        'dedication_stats': dedication_stats,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'portal/reports.html', context)

@login_required
def download_pdf_report(request):
    # 1. Capture Filter Dates from URL
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 2. Define Querysets
    b_qs = Baptism.objects.all()
    d_qs = Dedication.objects.all()
    t_qs = MemberTransfer.objects.all() # Define the missing variable
    c_qs = HolyCommunion.objects.all()

    # 3. Apply Filters
    if start_date and end_date:
        b_qs = b_qs.filter(ceremony_date__range=[start_date, end_date])
        d_qs = d_qs.filter(ceremony_date__range=[start_date, end_date])
        t_qs = t_qs.filter(date_completed__range=[start_date, end_date])
        c_qs = c_qs.filter(date__range=[start_date, end_date])

    # 4. Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    filename = f"Newlife_Report_{start_date}_to_{end_date}.pdf" if start_date else "Full_Report.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(300, 750, "NEWLIFE SDA CHURCH")
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(300, 730, "CLERK'S MINISTRY REPORT")
    
    p.setFont("Helvetica", 10)
    period = f"{start_date} to {end_date}" if start_date else "All Time"
    p.drawString(70, 700, f"Report Period: {period}")
    p.drawString(70, 685, f"Generated: {datetime.date.today()}")
    p.line(70, 680, 530, 680)

    # Statistical Summary Section
    p.setFont("Helvetica-Bold", 12)
    p.drawString(70, 640, "STATISTICAL SUMMARY")
    p.setFont("Helvetica", 12)
    p.drawString(70, 620, f"• Total Baptisms: {b_qs.count()}")
    p.drawString(70, 600, f"• Total Child Dedications: {d_qs.count()}")
    
    # Transfers Section
    p.drawString(70, 580, f"• Incoming Transfers (Finalized): {t_qs.filter(transfer_type='IN').count()}")
    p.drawString(70, 560, f"• Outgoing Transfers (Finalized): {t_qs.filter(transfer_type='OUT').count()}")
    
    # Communion Section
    communion_total = c_qs.aggregate(Sum('participants_count'))['participants_count__sum'] or 0
    p.drawString(70, 540, f"• Total Holy Communion Participants: {communion_total}")
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(70, 480, "Signed: __________________________ (Church Clerk)")

    p.showPage()
    p.save()
    return response


@login_required
def reports_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Fetch basic querysets
    b_qs = Baptism.objects.all()
    d_qs = Dedication.objects.all()
    t_qs = MemberTransfer.objects.all()

    if start_date and end_date:
        b_qs = b_qs.filter(ceremony_date__range=[start_date, end_date])
        d_qs = d_qs.filter(ceremony_date__range=[start_date, end_date])
        # For transfers, we filter by the date they were completed/finalized
        t_qs = t_qs.filter(date_completed__range=[start_date, end_date])

    # 1. Manual Python Counting for Months (Baptisms & Dedications)
    month_map = {i: name for i, name in enumerate(['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])}
    
    b_counts = {i: 0 for i in range(1, 13)}
    d_counts = {i: 0 for i in range(1, 13)}

    for b in b_qs: b_counts[b.ceremony_date.month] += 1
    for d in d_qs: d_counts[d.ceremony_date.month] += 1

    baptism_stats = [{'month_name': month_map[m], 'total': c} for m, c in b_counts.items() if c > 0]
    dedication_stats = [{'month_name': month_map[m], 'total': c} for m, c in d_counts.items() if c > 0]

    # 2. Transfer Totals (Incoming vs Outgoing)
    incoming_total = t_qs.filter(transfer_type='IN').count()
    outgoing_total = t_qs.filter(transfer_type='OUT').count()

    context = {
        'baptism_stats': baptism_stats,
        'dedication_stats': dedication_stats,
        'incoming_total': incoming_total,
        'outgoing_total': outgoing_total,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'portal/reports.html', context)