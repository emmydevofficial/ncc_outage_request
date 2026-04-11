from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Q
from .models import ACC, Region
from stations.models import Station
import csv
import io

# View all regions
def all_regions(request):
    regions = Region.objects.none()  # Default to empty queryset

    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_approver:
            # Admins and Approvers see all
            regions = Region.objects.all()
        elif request.user.is_reviewer or request.user.is_operator:
            # Reviewers and Operators see only their assigned region
            user_region = getattr(request.user, "region", None)
            if user_region:
                regions = Region.objects.filter(id=user_region.id)

    # Optional search filter
    search_query = request.GET.get("search", "").strip()
    if search_query:
        regions = regions.filter(
            Q(name__icontains=search_query) |
            Q(rom_name__icontains=search_query) |
            Q(roc_name__icontains=search_query)
        )
        
    context = {"regions": regions}
    return render(request, "regions/all_regions.html", context)

# View all ACCs
def all_accs(request):
    accs = ACC.objects.none()  # Default to empty queryset
    regions = Region.objects.all()

    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_approver:
            # Admins and Approvers see all ACCs
            accs = ACC.objects.all()
        elif request.user.is_reviewer:
            # Reviewers see ACCs in their region
            user_region = getattr(request.user, "region", None)
            if user_region:
                accs = ACC.objects.filter(region=user_region)
        elif request.user.is_operator:
            # Operators see ACCs in their station's region
            user_station = getattr(request.user, "station", None)
            if user_station and user_station.region:
                accs = ACC.objects.filter(region=user_station.region)

    # Optional filtering
    region_id = request.GET.get("region")
    search_query = request.GET.get("search", "").strip()

    if region_id:
        accs = accs.filter(region_id=region_id)

    if search_query:
        accs = accs.filter(
            Q(name__icontains=search_query)
        )
    
    
    context = {"accs" : accs, "regions" : regions}
    return render(request, "regions/all_accs.html", context)

# Add Region View
def add_region(request):
    return render(request, "regions/add_region.html")

# Add ACC View
def add_acc(request):
    regions = Region.objects.all()
    return render(request, "regions/add_acc.html", {"regions": regions})

# Get All ACC in a Region
def get_accs(request):
    region_id = request.GET.get('region_id')
    accs = ACC.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(accs), safe=False)

# Get All Station in a ACC
def get_stations(request):
    acc_id = request.GET.get('acc_id')
    stations = Station.objects.filter(acc_id=acc_id).values('id', 'name')
    return JsonResponse(list(stations), safe=False)

# Get All Station in a ACC
def get_stations_by_region(request):
    region_id = request.GET.get('region_id')
    stations = Station.objects.filter(region=region_id).values('id', 'name')
    return JsonResponse(list(stations), safe=False)

# Add Region Post Request
def add_region_post(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "").strip()
        rom_name = request.POST.get("rom_name", "").strip()
        rom_email = request.POST.get("rom_email", "").strip()
        rom_phone = request.POST.get("rom_phone", "").strip()
        roc_name = request.POST.get("roc_name", "").strip()
        roc_email = request.POST.get("roc_email", "").strip()
        roc_phone = request.POST.get("roc_phone", "").strip()

        if not name or not address or not rom_name or not rom_email or not rom_phone:
            messages.error(request, "All fields are required.")
            return redirect("add_region")

        if Region.objects.filter(name=name).exists():
            messages.error(request, "Region name already exists. Choose another.")
            return redirect("add_region")

        try:
            validate_email(rom_email)
            validate_email(roc_email)
        except ValidationError:
            messages.error(request, "Invalid email format for ROM or ROC.")
            return redirect("add_region")

        if not rom_phone.isdigit() or not roc_phone.isdigit():
            messages.error(request, "Phone numbers must contain only digits.")
            return redirect("add_region")

        region = Region(
            name=name, address=address, rom_name=rom_name,
            rom_email=rom_email, rom_phone=rom_phone, 
            roc_name=roc_name, roc_email=roc_email, roc_phone=roc_phone,
        )
        region.save()
        messages.success(request, "Region added successfully!")
        return redirect("all_regions")

# Add ACC Post Request
def add_acc_post(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        state = request.POST.get("state", "").strip()
        address = request.POST.get("address", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        region_id = request.POST.get("region", "").strip()

        if not name or not state or not address or not email or not phone or not region_id:
            messages.error(request, "All fields are required.")
            return redirect("add_acc")

        if ACC.objects.filter(name=name).exists():
            messages.error(request, "ACC name already exists. Choose another.")
            return redirect("add_acc")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect("add_acc")

        if not phone.isdigit():
            messages.error(request, "Phone number must contain only digits.")
            return redirect("add_acc")

        region = get_object_or_404(Region, id=region_id)

        acc = ACC(
            name=name, state=state, location=address,
            email=email, phone_num=phone, region=region,
        )
        acc.save()
        messages.success(request, "ACC added successfully!")
        return redirect("all_accs")

# Edit Region (GET)
def edit_region(request, region_id):
    region = get_object_or_404(Region, id=region_id)
    return render(request, "regions/edit_region.html", {"region": region})

# Edit Region (POST)
def edit_region_post(request, region_id):
    region = get_object_or_404(Region, id=region_id)
    if request.method == "POST":
        region.name = request.POST.get("name", "").strip()
        region.address = request.POST.get("address", "").strip()
        region.rom_name = request.POST.get("rom_name", "").strip()
        region.rom_email = request.POST.get("rom_email", "").strip()
        region.rom_phone = request.POST.get("rom_phone", "").strip()
        region.roc_name = request.POST.get("roc_name", "").strip()
        region.roc_email = request.POST.get("roc_email", "").strip()
        region.roc_phone = request.POST.get("roc_phone", "").strip()
        region.save()
        messages.success(request, "Region updated successfully!")
        return redirect("all_regions")

# Delete Region
def delete_region(request, region_id):
    region = get_object_or_404(Region, id=region_id)
    region.delete()
    messages.success(request, "Region deleted successfully!")
    return redirect("all_regions")

# Edit ACC (GET)
def edit_acc(request, acc_id):
    acc = get_object_or_404(ACC, id=acc_id)
    regions = Region.objects.all()
    return render(request, "regions/edit_acc.html", {"acc": acc, "regions": regions})

# Edit ACC (POST)
def edit_acc_post(request, acc_id):
    acc = get_object_or_404(ACC, id=acc_id)
    if request.method == "POST":
        acc.name = request.POST.get("name", "").strip()
        acc.state = request.POST.get("state", "").strip()
        acc.location = request.POST.get("address", "").strip()
        acc.email = request.POST.get("email", "").strip()
        acc.phone_num = request.POST.get("phone", "").strip()
        region_id = request.POST.get("region", "").strip()
        acc.region = get_object_or_404(Region, id=region_id)
        acc.save()
        messages.success(request, "ACC updated successfully!")
        return redirect("all_accs")

# Delete ACC
def delete_acc(request, acc_id):
    acc = get_object_or_404(ACC, id=acc_id)
    acc.delete()
    messages.success(request, "ACC deleted successfully!")
    return redirect("all_accs")

REG_EXPECTED_HEADERS = [
    "region", "address", "rom_name", "rom_email", "rom_phone",
    "roc_name", "roc_email", "roc_phone", "short_code"
]

def bulk_region_post(request):
    if request.method == "POST" and request.FILES.get("region_csv"):
        file = request.FILES["region_csv"]

        if not file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are allowed.")
            return redirect("bulk_upload")

        try:
            data = file.read().decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(data))

            # Normalize headers
            headers = [h.strip().lower() for h in csv_reader.fieldnames]
            if headers != REG_EXPECTED_HEADERS:
                messages.error(request, f"CSV headers are incorrect. Expected: {', '.join(REG_EXPECTED_HEADERS)}")
                return redirect("bulk_upload")

            success_count = 0
            skipped_duplicates = 0
            error_count = 0

            for row in csv_reader:
                try:
                    name = row["region"].strip()

                    # Skip if region name already exists
                    if Region.objects.filter(name=name).exists():
                        skipped_duplicates += 1
                        continue

                    # Clean and extract other values
                    address = row["address"].strip()
                    rom_name = row["rom_name"].strip()
                    rom_email = row["rom_email"].strip()
                    rom_phone = row["rom_phone"].strip()
                    roc_name = row["roc_name"].strip()
                    roc_email = row["roc_email"].strip()
                    roc_phone = row["roc_phone"].strip()
                    short_code = row["short_code"].strip()

                    # Validate required fields
                    if not all([name, address, rom_name, rom_email, rom_phone]):
                        raise ValueError("Missing required fields")

                    # Validate emails and phones
                    validate_email(rom_email)
                    validate_email(roc_email)

                    if not rom_phone.isdigit() or not roc_phone.isdigit():
                        raise ValueError("Phone numbers must be digits only")

                    # Create the region
                    Region.objects.create(
                        name=name,
                        address=address,
                        rom_name=rom_name,
                        rom_email=rom_email,
                        rom_phone=rom_phone,
                        roc_name=roc_name,
                        roc_email=roc_email,
                        roc_phone=roc_phone,
                        short_code=short_code
                    )
                    success_count += 1

                except (ValidationError, ValueError) as e:
                    error_count += 1
                    continue

            messages.success(
                request,
                f"{success_count} regions added. {skipped_duplicates} skipped (duplicates). {error_count} failed (invalid)."
            )
            return redirect("all_regions")

        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect("bulk_upload")

    else:
        messages.error(request, "Please upload a valid CSV file.")
        return redirect("bulk_upload")


ACC_EXPECTED_HEADERS = ["region", "acc", "email", "location", "state", "phone"]

def bulk_acc_post(request):
    if request.method == "POST" and request.FILES.get("acc_csv"):
        file = request.FILES["acc_csv"]

        if not file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are allowed.")
            return redirect("add_acc")  # Replace with your actual URL name

        try:
            data = file.read().decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(data))

            headers = [h.strip().lower() for h in csv_reader.fieldnames]
            if headers != ACC_EXPECTED_HEADERS:
                messages.error(request, f"CSV headers are incorrect. Expected: {', '.join(ACC_EXPECTED_HEADERS)}")
                return redirect("add_acc")

            success_count = 0
            skipped_missing_region = 0
            skipped_duplicates = 0
            error_count = 0

            for row in csv_reader:
                try:
                    region_name = row["region"].strip()
                    acc_name = row["acc"].strip()
                    email = row["email"].strip()
                    location = row["location"].strip()
                    state = row["state"].strip()
                    phone = row["phone"].strip()

                    # Check if region exists
                    try:
                        region = Region.objects.get(name=region_name)
                    except Region.DoesNotExist:
                        skipped_missing_region += 1
                        continue

                    # Check if ACC already exists
                    if ACC.objects.filter(name=acc_name).exists():
                        skipped_duplicates += 1
                        continue

                    # Validate email
                    validate_email(email)

                    # Validate phone (digits only)
                    if not phone.isdigit():
                        raise ValueError("Phone number must be digits only")

                    # Create ACC
                    ACC.objects.create(
                        name=acc_name,
                        region=region,
                        email=email,
                        location=location,
                        state=state,
                        phone_num=phone
                    )
                    success_count += 1

                except (ValidationError, ValueError) as e:
                    error_count += 1
                    continue

            messages.success(
                request,
                f"{success_count} ACCs added. {skipped_duplicates} skipped (duplicates), {skipped_missing_region} skipped (missing region), {error_count} invalid."
            )
            return redirect("all_accs")  # Replace with your actual redirect

        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect("add_acc")

    else:
        messages.error(request, "Please upload a valid CSV file.")
        return redirect("add_acc")
