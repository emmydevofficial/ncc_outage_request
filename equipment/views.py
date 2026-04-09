from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Equipment, Lines
from stations.models import Station
from regions.models import Region, ACC

# View all equipments
def all_equipments(request):
    equipments = Equipment.objects.all()
    regions =  Region.objects.all()
    accs = ACC.objects.all()
    stations = Station.objects.all()
    
    region_id = request.GET.get("region")
    acc_id = request.GET.get("acc")
    station_id = request.GET.get("station")
    search_query = request.GET.get("search", "").strip()
    
    if region_id:
        equipments = equipments.filter(station__region_id=region_id)
        accs = accs.filter(region_id = region_id)
        stations = stations.filter(region_id=region_id)
    if acc_id:
        equipments = equipments.filter(station__acc_id=acc_id)
        stations = stations.filter(acc_id=acc_id)
    if station_id:
        equipments = equipments.filter(station_id = station_id)
        
    if search_query:
        equipments = equipments.filter(
            Q(name__icontains=search_query) |
            Q(nomenclature__icontains=search_query) |
            Q(volttage_level__icontains=search_query) |
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
                volttage_level=voltage_level,
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
        equipment.volttage_level = request.POST.get("voltage_level")
        station_id = request.POST.get("station")
        equipment.equipment_type = request.POST.get("equipment_type")
        equipment.approve_date = request.POST.get("approve_date")
        
        if not all([equipment.name, equipment.nomenclature, equipment.volttage_level, station_id, equipment.equipment_type, equipment.approve_date]):
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

# Delete line
def delete_line(request, line_id):
    line = get_object_or_404(Lines, id=line_id)
    line.delete()
    messages.success(request, "Line deleted successfully!")
    return redirect("all_lines")
