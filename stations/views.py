from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Station
from regions.models import Region, ACC
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import csv
import io

# View all stations
def all_stations(request):
    stations = Station.objects.all()
    regions = Region.objects.all()
    accs = ACC.objects.all()
    
    region_id = request.GET.get("region")
    acc_id = request.GET.get("acc")
    search_query = request.GET.get("search", "").strip()
    
    if region_id:
        stations = stations.filter(region_id=region_id)
        accs = accs.filter(region_id = region_id)
    if acc_id:
        stations = stations.filter(acc_id=acc_id)
        
    if search_query:
        stations = stations.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)            
        )
    
    
    context = {"stations": stations, "regions":regions, "accs":accs}
    return render(request, "stations/all_stations.html", context)

# Add station form
def add_station(request):
    regions = Region.objects.all()
    accs = ACC.objects.all()
    context = {"regions": regions, "accs": accs}
    return render(request, "stations/add_station.html", context)

# Add station - Handle POST request
def add_station_post(request):
    if request.method == "POST":
        name = request.POST.get("name")
        voltage = request.POST.get("voltage")
        state = request.POST.get("state")
        location = request.POST.get("location")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        region_id = request.POST.get("region")  
        acc_id = request.POST.get("acc") 

        if not all([name, voltage, state, location, email, phone, region_id, acc_id]):
            messages.error(request, "All fields are required.")
            return redirect("add_station")  

        if Station.objects.filter(email=email).exists():
            messages.error(request, "A station with this email already exists.")
            return redirect("add_station")

        try:
            region = Region.objects.get(id=region_id)  
            acc = ACC.objects.get(id=acc_id)
            Station.objects.create(
                name=name,
                voltage_level=voltage,
                state=state,
                location=location,
                email=email,
                phone_num=phone,
                region=region,
                acc=acc,
            )
            messages.success(request, "Station added successfully!")
            return redirect("all_stations")

        except Region.DoesNotExist:
            messages.error(request, "Invalid Region selected.")
            return redirect("add_station")
        
        except ACC.DoesNotExist:
            messages.error(request, "Invalid ACC selected.")
            return redirect("add_station")

# Edit station form (GET)
def edit_station(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    regions = Region.objects.all()
    accs = ACC.objects.all()
    context = {"station": station, "regions": regions, "accs": accs}
    return render(request, "stations/edit_station.html", context)

# Edit station - Handle POST request
def edit_station_post(request, station_id):
    station = get_object_or_404(Station, id=station_id)

    if request.method == "POST":
        station.name = request.POST.get("name")
        station.voltage_level = request.POST.get("voltage")
        station.state = request.POST.get("state")
        station.location = request.POST.get("location")
        station.email = request.POST.get("email")
        station.phone_num = request.POST.get("phone")
        region_id = request.POST.get("region")
        acc_id = request.POST.get("acc")

        if not all([station.name, station.voltage_level, station.state, station.location, station.email, station.phone_num, region_id, acc_id]):
            messages.error(request, "All fields are required.")
            return redirect("edit_station", station_id=station.id)

        try:
            station.region = Region.objects.get(id=region_id)
            station.acc = ACC.objects.get(id=acc_id)
            station.save()
            messages.success(request, "Station updated successfully!")
            return redirect("all_stations")

        except Region.DoesNotExist:
            messages.error(request, "Invalid Region selected.")
            return redirect("edit_station", station_id=station.id)

        except ACC.DoesNotExist:
            messages.error(request, "Invalid ACC selected.")
            return redirect("edit_station", station_id=station.id)

STN_EXPECTED_HEADERS = [
    "region", "acc", "station", "voltage_level",
    "location", "state", "email", "phone"
]

def bulk_station_post(request):
    if request.method == "POST" and request.FILES.get("station_csv"):
        file = request.FILES["station_csv"]

        if not file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are allowed.")
            return redirect("bulk_upload")  # Replace with actual view name

        try:
            data = file.read().decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(data))

            headers = [h.strip().lower() for h in csv_reader.fieldnames]
            if headers != STN_EXPECTED_HEADERS:
                messages.error(request, f"CSV headers are incorrect. Expected: {', '.join(STN_EXPECTED_HEADERS)}")
                return redirect("bulk_upload")

            success_count = 0
            skipped_missing_fk = 0
            skipped_duplicates = 0
            error_count = 0

            for row in csv_reader:
                try:
                    region_name = row["region"].strip()
                    acc_name = row["acc"].strip()
                    station_name = row["station"].strip()
                    voltage = row["voltage_level"].strip()
                    location = row["location"].strip()
                    state = row["state"].strip()
                    email = row["email"].strip()
                    phone = row["phone"].strip()

                    # Check if region exists
                    try:
                        region = Region.objects.get(name=region_name)
                    except Region.DoesNotExist:
                        skipped_missing_fk += 1
                        continue

                    # Check if acc exists
                    try:
                        acc = ACC.objects.get(name=acc_name)
                    except ACC.DoesNotExist:
                        skipped_missing_fk += 1
                        continue

                    # Check station name uniqueness
                    if Station.objects.filter(name=station_name).exists():
                        skipped_duplicates += 1
                        continue

                    # Validate email
                    validate_email(email)

                    # Validate phone
                    if not phone.isdigit():
                        raise ValueError("Phone number must contain digits only.")

                    # Create station
                    Station.objects.create(
                        name=station_name,
                        voltage_level=voltage,
                        region=region,
                        acc=acc,
                        location=location,
                        state=state,
                        email=email,
                        phone_num=phone
                    )
                    success_count += 1

                except (ValidationError, ValueError) as e:
                    error_count += 1
                    continue

            messages.success(
                request,
                f"{success_count} stations added. "
                f"{skipped_duplicates} skipped (duplicates), "
                f"{skipped_missing_fk} skipped (missing region/acc), "
                f"{error_count} failed (invalid)."
            )
            return redirect("all_stations")  # Replace with your success URL

        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect("bulk_upload")

    else:
        messages.error(request, "Please upload a valid CSV file.")
        return redirect("bulk_upload")

# Delete station
def delete_station(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    station.delete()
    messages.success(request, "Station deleted successfully!")
    return redirect("all_stations")
