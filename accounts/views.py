from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Staff
from stations.models import Station
from regions.models import Region, ACC

def all_users(request):
    users = Staff.objects.all()
    regions = Region.objects.all()
    stations = Station.objects.all()

    region_id = request.GET.get("region")
    station_id = request.GET.get("station")
    search_query = request.GET.get("search", "").strip()

    if region_id:
        users = users.filter(station__region_id=region_id)
        stations = stations.filter(region_id = region_id)
    if station_id:
        users = users.filter(station_id=station_id)
    
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(staff_no__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    context = {
        "users": users,
        "regions": regions,
        "stations": stations,
        "search_query": search_query
    }
    return render(request, "operators/all_users.html", context)


def add_user(request):
    regions = Region.objects.all()
    stations = Station.objects.all()
    accs = ACC.objects.all()
    
    context = {"regions" : regions, "stations" : stations, "accs":accs}
    return render(request, "operators/add_user.html", context)


def add_user_post(request):
    regions = Region.objects.all()
    stations = Station.objects.all()
    context = {"regions" : regions, "stations" : stations}
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        staff_no = request.POST.get("staff_no", "").strip()
        phone_num = request.POST.get("phone", "").strip()

        station_id = request.POST.get("station")
        region_id = request.POST.get("region")

        is_station_supervisor = request.POST.get("station_supervisor") == "on"
        is_reviewer = request.POST.get("reviewer") == "on"
        is_approver = request.POST.get("approval") == "on"
        is_operator = request.POST.get("operator") == "on"
        is_admin = request.POST.get("admin") == "on"

        if not first_name or not last_name or not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("add_user")

        if Staff.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Choose another.")
            return redirect("add_user")

        if Staff.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("add_user")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect("add_user")

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect("add_user")

        if phone_num and not phone_num.isdigit():
            messages.error(request, "Phone number must contain only digits.")
            return redirect("add_user")

        station = Station.objects.filter(id=station_id).first() if station_id else None
        region = Region.objects.filter(id=region_id).first() if region_id else None

        user = Staff(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            staff_no=staff_no,
            phone_num=phone_num,
            station=station,
            region=region,
            is_station_supervisor=is_station_supervisor,
            is_reviewer=is_reviewer,
            is_approver=is_approver,
            is_operator=is_operator,
            is_admin=is_admin,
        )
        
        user.set_password(password)
        user.save()
        
        print(username)
        print(password)

        messages.success(request, "User created successfully!")
        return redirect("all_users")

    return render(request, "operators/add_user.html", context)

def edit_user(request, user_id):
    user = get_object_or_404(Staff, id=user_id)
    stations = Station.objects.all()
    regions = Region.objects.all()
    accs = ACC.objects.all()

    return render(request, "operators/edit_user.html", {
        "user": user,
        "stations": stations,
        "regions": regions,
        "accs": accs
    })

def edit_user_post(request, user_id):
    user = get_object_or_404(Staff, id=user_id)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.username = request.POST.get("username", "").strip()
        user.email = request.POST.get("email", "").strip()
        user.staff_no = request.POST.get("staff_no", "").strip()
        user.phone_num = request.POST.get("phone", "").strip()

        station_id = request.POST.get("station")
        region_id = request.POST.get("region")

        user.is_station_supervisor = request.POST.get("station_supervisor") == "on"
        user.is_reviewer = request.POST.get("reviewer") == "on"
        user.is_approver = request.POST.get("approval") == "on"
        user.is_operator = request.POST.get("operator") == "on"
        user.is_admin = request.POST.get("admin") == "on"

        if not user.first_name or not user.last_name or not user.username or not user.email:
            messages.error(request, "All fields are required.")
            return redirect("edit_user", user_id=user.id)

        try:
            validate_email(user.email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect("edit_user", user_id=user.id)

        if user.phone_num and not user.phone_num.isdigit():
            messages.error(request, "Phone number must contain only digits.")
            return redirect("edit_user", user_id=user.id)

        if station_id:
            user.station = Station.objects.filter(id=station_id).first()
        if region_id:
            user.region = Region.objects.filter(id=region_id).first()

        new_password = request.POST.get("password", "").strip()
        if new_password:
            if len(new_password) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
                return redirect("edit_user", user_id=user.id)
            user.set_password(new_password)

        user.save()

        messages.success(request, "User updated successfully!")
        return redirect("all_users")

    return redirect("edit_user", user_id=user.id)

def delete_user(request, user_id):
    user = get_object_or_404(Staff, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect("all_users")

def login_user(request):
    return render(request, "operators/login.html")

def login_post(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
                
        user = authenticate(request, username=username, password=password)
         
       
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")  # Redirect to a protected page
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login_user")

def user_logout(request):
    logout(request)
    return redirect("login_user") 
