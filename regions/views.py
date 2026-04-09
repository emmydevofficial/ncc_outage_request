from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Q
from .models import ACC, Region
from stations.models import Station

# View all regions
def all_regions(request):
    regions = Region.objects.all()
    
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
    accs = ACC.objects.all()
    regions = Region.objects.all()
    
    region_id = request.GET.get("region")
    search_query = request.GET.get("search", "").strip()
    
    if region_id:
        accs = accs.filter(region=region_id)            
    
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
