from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Equipment, Lines
from stations.models import Station
from regions.models import Region, ACC
import csv
import io
import datetime

# View all equipments
def all_equipments(request):
    equipments = Equipment.objects.none()
    regions = Region.objects.all()
    accs = ACC.objects.none()
    stations = Station.objects.none()

    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_approver:
            # Admins and Approvers: Full access
            equipments = Equipment.objects.all()
            accs = ACC.objects.all()
            stations = Station.objects.all()
        elif request.user.is_reviewer:
            # Reviewers: Equipment in their region (via station)
            user_region = getattr(request.user, "region", None)
            if user_region:
                equipments = Equipment.objects.filter(station__region=user_region)
                accs = ACC.objects.filter(region=user_region)
                stations = Station.objects.filter(region=user_region)
        elif request.user.is_operator:
            # Operators: Equipment in their station only
            user_station = getattr(request.user, "station", None)
            if user_station:
                equipments = Equipment.objects.filter(station=user_station)
                accs = ACC.objects.filter(id=user_station.acc_id)
                stations = Station.objects.filter(id=user_station.id)        
    
    # Filters
    region_id = request.GET.get("region")
    acc_id = request.GET.get("acc")
    station_id = request.GET.get("station")
    search_query = request.GET.get("search", "").strip()

    if region_id:
        equipments = equipments.filter(station__region_id=region_id)
        accs = accs.filter(region_id=region_id)
        stations = stations.filter(region_id=region_id)
    if acc_id:
        equipments = equipments.filter(station__acc_id=acc_id)
        stations = stations.filter(acc_id=acc_id)
    if station_id:
        equipments = equipments.filter(station_id=station_id)

    if search_query:
        equipments = equipments.filter(
            Q(name__icontains=search_query) |
            Q(nomenclature__icontains=search_query) |
            Q(voltage_level__icontains=search_query) |
            Q(equipment_type__icontains=search_query)
        )
        
    context = {"equipments": equipments, 
               "stations":stations, 
               "accs":accs, 
               "regions":regions}
    return render(request, "equipments/all_equipments.html", context)

# Add equipment form
def add_equipment(request):
    regions =  Region.objects.all()
    stations = Station.objects.all()
    context = {"stations": stations, "regions":regions}
    return render(request, "equipments/add_equipment.html", context)

# Add equipment - Handle POST request
def add_equipment_post(request):
    if request.method == "POST":
        name = request.POST.get("name")
        nomenclature = request.POST.get("nomenclature")
        voltage_level = request.POST.get("voltage_level")
        station_id = request.POST.get("station")
        equipment_type = request.POST.get("equipment_type")
        approve_date = request.POST.get("approve_date")
        
        if not all([name, nomenclature, voltage_level, station_id, approve_date]):
            messages.error(request, "All fields are required.")
            return redirect("add_equipment")
        
        try:
            station = Station.objects.get(id=station_id)
            Equipment.objects.create(
                name=name,
                nomenclature=nomenclature,
                voltage_level=voltage_level,
                equipment_type = equipment_type,
                station=station,
                approve_date = approve_date
            )
            messages.success(request, "Equipment added successfully!")
            return redirect("all_equipments")
        except Station.DoesNotExist:
            messages.error(request, "Invalid Station selected.")
            return redirect("add_equipment")

# Edit equipment form (GET)
def edit_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    regions =  Region.objects.all()
    stations = Station.objects.all()
    context = {"equipment": equipment, "stations": stations, "regions":regions}
    return render(request, "equipments/edit_equipment.html", context)

# Edit equipment - Handle POST request
def edit_equipment_post(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == "POST":
        equipment.name = request.POST.get("name")
        equipment.nomenclature = request.POST.get("nomenclature")
        equipment.voltage_level = request.POST.get("voltage_level")
        station_id = request.POST.get("station")
        equipment.equipment_type = request.POST.get("equipment_type")
        equipment.approve_date = request.POST.get("approve_date")
        
        if not all([equipment.name, equipment.nomenclature, equipment.voltage_level, station_id, equipment.equipment_type, equipment.approve_date]):
            messages.error(request, "All fields are required.")
            return redirect("edit_equipment", equipment_id=equipment.id)
        
        try:
            equipment.station = Station.objects.get(id=station_id)
            equipment.save()
            messages.success(request, "Equipment updated successfully!")
            return redirect("all_equipments")
        except Station.DoesNotExist:
            messages.error(request, "Invalid Station selected.")
            return redirect("edit_equipment", equipment_id=equipment.id)

# Delete equipment
def delete_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    equipment.delete()
    messages.success(request, "Equipment deleted successfully!")
    return redirect("all_equipments")

# View all lines
def all_lines(request):
    lines = Lines.objects.all()
    regions =  Region.objects.all()
    accs = ACC.objects.all()
    stations = Station.objects.all()
    
    region_id = request.GET.get("region")
    acc_id = request.GET.get("acc")
    station_id = request.GET.get("station")
    search_query = request.GET.get("search", "").strip()
    
    if region_id:
        lines = lines.filter(station__region_id=region_id)
        accs = accs.filter(region_id = region_id)
        stations = stations.filter(region_id=region_id)
    if acc_id:
        lines = lines.filter(station__acc_id=acc_id)
        stations = stations.filter(acc_id=acc_id)
    if station_id:
        lines = lines.filter(station_id = station_id)
        
    if search_query:
        lines = lines.filter(
            Q(name__icontains=search_query) |
            Q(nomenclature__icontains=search_query) |
            Q(voltage_level__icontains=search_query) |
            Q(line_type__icontains=search_query)                
        )
        
    context = {"lines": lines, 
               "stations":stations, 
               "accs":accs, 
               "regions":regions}
    return render(request, "equipments/all_lines.html", context)

# Add line form
def add_line(request):
    stations = Station.objects.all()
    regions =  Region.objects.all()
    context = {"stations": stations, "regions":regions}
    return render(request, "equipments/add_line.html", context)

# Add line - Handle POST request
def add_line_post(request):
    if request.method == "POST":
        name = request.POST.get("name")
        nomenclature = request.POST.get("nomenclature")
        voltage_level = request.POST.get("voltage_level")
        line_type = request.POST.get("line_type")
        station_id = request.POST.get("station")
        approve_date = request.POST.get("approve_date")
        
        
        if not all([name, nomenclature, voltage_level, line_type, station_id, approve_date]):
            messages.error(request, "All fields are required.")
            return redirect("add_line")
        
        try:
            station = Station.objects.get(id=station_id)
            Lines.objects.create(
                name=name,
                nomenclature=nomenclature,
                voltage_level=voltage_level,
                line_type=line_type,
                station=station,
                approve_date=approve_date
            )
            messages.success(request, "Line added successfully!")
            return redirect("all_lines")
        except Station.DoesNotExist:
            messages.error(request, "Invalid Station selected.")
            return redirect("add_line")

# Edit line form (GET)
def edit_line(request, line_id):
    line = get_object_or_404(Lines, id=line_id)
    regions =  Region.objects.all()
    stations = Station.objects.all()
    context = {"line": line, "stations": stations, "regions":regions}
    return render(request, "equipments/edit_line.html", context)

# Edit line - Handle POST request
def edit_line_post(request, line_id):
    line = get_object_or_404(Lines, id=line_id)

    if request.method == "POST":
        line.name = request.POST.get("name")
        line.nomenclature = request.POST.get("nomenclature")
        line.voltage_level = request.POST.get("voltage_level")
        line.line_type = request.POST.get("line_type")
        line.approve_date = request.POST.get("approve_date")
        station_id = request.POST.get("station")
        
        if not all([line.name, line.nomenclature, line.voltage_level, line.line_type, station_id, line.approve_date]):
            messages.error(request, "All fields are required.")
            return redirect("edit_line", line_id=line.id)
        
        try:
            line.station = Station.objects.get(id=station_id)
            line.save()
            messages.success(request, "Line updated successfully!")
            return redirect("all_lines")
        except Station.DoesNotExist:
            messages.error(request, "Invalid Station selected.")
            return redirect("edit_line", line_id=line.id)

EQT_EXPECTED_HEADERS = [
    "region", "acc", "station", "equipment",
    "equipment_type", "voltage_level", "nomenclature"
]

def bulk_equipment_post(request):
    if request.method == "POST" and request.FILES.get("equipment_csv"):
        file = request.FILES["equipment_csv"]

        if not file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are allowed.")
            return redirect("bulk_upload")  # Update with your actual view name

        try:
            data = file.read().decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(data))

            headers = [h.strip().lower() for h in csv_reader.fieldnames]
            if headers != EQT_EXPECTED_HEADERS:
                messages.error(request, f"CSV headers are incorrect. Expected: {', '.join(EQT_EXPECTED_HEADERS)}")
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
                    equipment_name = row["equipment"].strip()
                    equipment_type = row["equipment_type"].strip()
                    voltage = row["voltage_level"].strip()
                    nomenclature = row["nomenclature"].strip()

                    # Validate FK: Region
                    try:
                        region = Region.objects.get(name=region_name)
                    except Region.DoesNotExist:
                        skipped_missing_fk += 1
                        continue

                    # Validate FK: ACC
                    try:
                        acc = ACC.objects.get(name=acc_name)
                    except ACC.DoesNotExist:
                        skipped_missing_fk += 1
                        continue

                    # Validate FK: Station (must match region and acc too)
                    try:
                        station = Station.objects.get(
                            name=station_name,
                            region=region,
                            acc=acc
                        )
                    except Station.DoesNotExist:
                        skipped_missing_fk += 1
                        continue

                    # Unique check: station + equipment
                    if Equipment.objects.filter(station=station, name=equipment_name).exists():
                        skipped_duplicates += 1
                        continue

                    # Save equipment
                    Equipment.objects.create(
                        name=equipment_name,
                        equipment_type=equipment_type,
                        voltage_level=voltage,
                        nomenclature=nomenclature,
                        station=station
                    )
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    continue

            messages.success(
                request,
                f"{success_count} equipment added. "
                f"{skipped_duplicates} skipped (duplicate station+name), "
                f"{skipped_missing_fk} skipped (missing FK), "
                f"{error_count} failed (invalid rows)."
            )
            return redirect("all_equipments")  # Update accordingly

        except Exception as e:
            messages.error(request, f"Error reading file: {str(e)}")
            return redirect("bulk_upload")

    else:
        messages.error(request, "Upload a valid CSV file.")
        return redirect("bulk_upload")
    
SCHE_EXPECTED_HEADERS = [
    "station", "equipment", "equipment_type", "schedule_date"
]

def update_equipment_schedule(request):
    if request.method == "POST" and request.FILES.get("schedule_csv"):
        file = request.FILES["schedule_csv"]

        if not file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are allowed.")
            return redirect("bulk_upload")

        try:
            data = file.read().decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(data))

            headers = [h.strip().lower() for h in csv_reader.fieldnames]
            if headers != SCHE_EXPECTED_HEADERS:
                messages.error(request, f"CSV headers are incorrect. Expected: {', '.join(SCHE_EXPECTED_HEADERS)}")
                return redirect("bulk_upload")

            updated_count = 0
            skipped_not_found = 0
            invalid_date_count = 0

            for row in csv_reader:
                try:
                    station_name = row["station"].strip()
                    equipment_name = row["equipment"].strip()
                    schedule_date_str = row["schedule_date"].strip()

                    # Parse date
                    try:
                        schedule_date = datetime.datetime.strptime(schedule_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        invalid_date_count += 1
                        continue

                    # Get station
                    try:
                        station = Station.objects.get(name=station_name)
                    except Station.DoesNotExist:
                        skipped_not_found += 1
                        continue

                    # Get equipment by station + name
                    try:
                        equipment = Equipment.objects.get(name=equipment_name, station=station)
                        equipment.approve_date = schedule_date
                        equipment.save()
                        updated_count += 1
                    except Equipment.DoesNotExist:
                        skipped_not_found += 1
                        continue

                except Exception:
                    continue  # Silent fail to prevent crash per row

            messages.success(
                request,
                f"{updated_count} equipment updated. "
                f"{skipped_not_found} not found, "
                f"{invalid_date_count} invalid dates."
            )
            return redirect("all_equipments")  # Update accordingly

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            return redirect("bulk_upload")

    else:
        messages.error(request, "Please upload a valid CSV file.")
        return redirect("bulk_upload")


# Delete line
def delete_line(request, line_id):
    line = get_object_or_404(Lines, id=line_id)
    line.delete()
    messages.success(request, "Line deleted successfully!")
    return redirect("all_lines")
