from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from requests.models import Request
from stations.models import Station
from regions.models import Region, ACC
from equipment.models import Equipment
from django.contrib.auth.decorators import login_required
import csv
from datetime import datetime

@login_required
def dashboard(request):
    # Get all requests sorted from latest to oldest
    requests = Request.objects.all().order_by("-created_at")
    regions = Region.objects.all()
    accs = ACC.objects.all()
    stations = Station.objects.all()

    # Filtering logic
    app_start_date = request.GET.get("app_start_date")
    app_end_date = request.GET.get("app_end_date")    
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    region = request.GET.get("region")
    acc = request.GET.get("acc")
    station = request.GET.get("station")
    work_description = request.GET.get("work_description")
    
    if app_start_date and app_end_date:
        # Convert from string to datetime
        app_start_date = datetime.strptime(app_start_date, "%Y-%m-%d")
        app_end_date = datetime.strptime(app_end_date, "%Y-%m-%d")

        # Only make naive datetimes aware
        if timezone.is_naive(app_start_date):
            app_start_date = timezone.make_aware(app_start_date)
        if timezone.is_naive(app_end_date):
            app_end_date = timezone.make_aware(app_end_date)

        # Apply the filter with timezone-aware datetimes
        requests = requests.filter(
            created_at__gte=app_start_date,
            created_at__lte=app_end_date
        )
    
    elif app_start_date:
        # When only app_start_date is provided, check that the created_at date matches exactly
        try:
            app_start_dt = datetime.strptime(app_start_date, "%Y-%m-%d")
            if timezone.is_naive(app_start_dt):
                app_start_dt = timezone.make_aware(app_start_dt)
            # Filter by the date portion of created_at
            requests = requests.filter(created_at__date=app_start_dt.date())
        except ValueError:
            pass  # Handle error or log it as needed


    if start_date and end_date:
        requests = requests.filter(start_date__gte=start_date, end_date__lte=end_date)
        
    elif start_date:
        # When only start_date is provided, filter for an exact match on start_date
        requests = requests.filter(start_date=start_date)


    if region:
        requests = requests.filter(station__region__id=region)
        accs = accs.filter(region=region)
        stations = stations.filter(region=region)

    if acc:
        requests = requests.filter(station__acc__id=acc)
        stations = stations.filter(acc=acc)

    if station:
        requests = requests.filter(station__id=station)

    if work_description:
        requests = requests.filter(work_description__icontains=work_description)

    # Count values
    request_count = requests.count()
    station_count = Station.objects.count()
    equipment_count = Equipment.objects.count()
    region_count = Region.objects.count()
    unreviewed_request_count = Request.objects.filter(is_reviewed=False).count()
    approved_request_count = Request.objects.filter(is_approved=True).count()

    # Restricting operators to only see their station's requests
    if not (request.user.is_admin or request.user.is_reviewer or request.user.is_approver):
        requests = requests.filter(station=request.user.station)
        request_count = requests.count()
        unreviewed_request_count = requests.filter(is_reviewed=False).count()
        approved_request_count = requests.filter(is_approved=True).count()

    count = {
        "request_count": request_count,
        "station_count": station_count,
        "equipment_count": equipment_count,
        "region_count": region_count,
        "unreviewed_request_count": unreviewed_request_count,
        "approved_request_count": approved_request_count,
    }

    context = {
        "requests": requests,
        "count": count,
        "regions": regions,
        "accs": accs,
        "stations": stations,
    }
    return render(request, "dashboard/index.html", context)


# CSV Export View
@login_required
def export_requests_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="requests.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Timestamp", "Region", "Request Station", "Relayed To NCC By",
        "Location Of Job", "Equipment Type", "Desired Equipment", "Outage Type",
        "Work Description", "Additional Apparatus", "Start Date", "Start Time",
        "End Date", "End Time", "Load Interrupted", "Areas Affected", "Remarks", "Disco/Genco Notified"
    ])

    # Get all requests sorted from latest to oldest
    requests = Request.objects.all().order_by("-created_at")
    accs = ACC.objects.all()
    stations = Station.objects.all()

    # Filtering logic
    app_start_date = request.GET.get("app_start_date")
    app_end_date = request.GET.get("app_end_date")    
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    region = request.GET.get("region")
    acc = request.GET.get("acc")
    station = request.GET.get("station")
    work_description = request.GET.get("work_description")
    
    if app_start_date and app_end_date:
        # Convert from string to datetime
        app_start_date = datetime.strptime(app_start_date, "%Y-%m-%d")
        app_end_date = datetime.strptime(app_end_date, "%Y-%m-%d")

        # Only make naive datetimes aware
        if timezone.is_naive(app_start_date):
            app_start_date = timezone.make_aware(app_start_date)
        if timezone.is_naive(app_end_date):
            app_end_date = timezone.make_aware(app_end_date)

        # Apply the filter with timezone-aware datetimes
        requests = requests.filter(
            created_at__gte=app_start_date,
            created_at__lte=app_end_date
        )
    
    elif app_start_date:
        # When only app_start_date is provided, check that the created_at date matches exactly
        try:
            app_start_dt = datetime.strptime(app_start_date, "%Y-%m-%d")
            if timezone.is_naive(app_start_dt):
                app_start_dt = timezone.make_aware(app_start_dt)
            # Filter by the date portion of created_at
            requests = requests.filter(created_at__date=app_start_dt.date())
        except ValueError:
            pass  # Handle error or log it as needed


    if start_date and end_date:
        requests = requests.filter(start_date__gte=start_date, end_date__lte=end_date)
        
    elif start_date:
        # When only start_date is provided, filter for an exact match on start_date
        requests = requests.filter(start_date=start_date)


    if region:
        requests = requests.filter(station__region__id=region)
        accs = accs.filter(region=region)
        stations = stations.filter(region=region)

    if acc:
        requests = requests.filter(station__acc__id=acc)
        stations = stations.filter(acc=acc)

    if station:
        requests = requests.filter(station__id=station)

    if work_description:
        requests = requests.filter(work_description__icontains=work_description)

    
    # Restricting operators to only see their station's requests
    if not (request.user.is_admin or request.user.is_reviewer or request.user.is_approver):
        requests = requests.filter(station=request.user.station)        

    # Write request data to CSV
    for req in requests:
        writer.writerow([
            req.created_at.strftime("%Y-%m-%d %H:%M"),
            req.station.region if req.station else "N/A",
            req.station.acc if req.station else "N/A",
            f"{req.user.last_name} {req.user.first_name}" if req.user else "N/A",
            req.station if req.station else "N/A",
            req.equipment.equipment_type if req.equipment else "N/A",
            req.equipment if req.equipment else "N/A",
            req.outage_type,
            req.work_description,
            req.apparatus_for_safe_working_space,
            req.start_date,
            req.start_time,
            req.end_date,
            req.end_time,
            req.load_involved,
            req.area_affected,
            req.remarks,
            req.disco_genco_notified
        ])

    return response

