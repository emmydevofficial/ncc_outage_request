from django.shortcuts import render, redirect, get_object_or_404
from equipment.models import Equipment, Lines
from django.contrib import messages
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .models import Request, RequestLog
from .loggings import log_request_action
from django.utils import timezone
from datetime import datetime
from regions.models import Region, ACC
from stations.models import Station
from django.http import HttpResponse, JsonResponse
from weasyprint import HTML
from django.db.models import Q
import platform

# Create your views here.
@login_required
def all_requests(request):
    requests = Request.objects.all()
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
    search = request.GET.get("search")

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

    if search:
        requests = requests.filter(
            Q(work_description__icontains=search) |
            Q(request_id__icontains=search)
            )
    
    # if not request.user.is_admin or not request.user.is_reviewer or not request.user.is_approver:
    #     requests = requests.filter(station=request.user.station)
    # Restricting operators to only see their station's requests
    if not (request.user.is_admin or request.user.is_reviewer or request.user.is_approver):
        requests = requests.filter(station=request.user.station)
        
    context = {
        "requests": requests,        
        "regions": regions,
        "accs": accs,
        "stations": stations,
    }
    return render(request, "requests/all_requests.html", context)


@login_required
def add_request(request):
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_reviewer or request.user.is_approver:
            # Admins, Approvers, Reviewers
            if request.user.is_reviewer:
                # Reviewer — only for equipment in user's region
                user_region = request.user.region
                equipments = Equipment.objects.filter(station__region=user_region)
                lines = Lines.objects.filter(station__region=user_region)
            else:
                # Admin or Approver — full access
                equipments = Equipment.objects.all()
                lines = Lines.objects.all()

            station = None  # Not tied to one station
        else:
            # Operator — only equipment in their station
            station = request.user.station
            equipments = Equipment.objects.filter(station=station)
            lines = Lines.objects.filter(station=station)

        context = {
            "user": request.user,
            "station": station,
            "equipments": equipments,
            "lines": lines,
        }
        return render(request, "requests/add_request.html", context)
    else:
        return redirect("login_user")
    

@login_required
def create_request(request):
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_reviewer or request.user.is_approver:
            # Admins, Approvers, Reviewers
            if request.user.is_reviewer:
                # Reviewer — only for equipment in user's region
                user_region = request.user.region
                equipments = Equipment.objects.filter(station__region=user_region)
                lines = Lines.objects.filter(station__region=user_region)
            else:
                # Admin or Approver — full access
                equipments = Equipment.objects.all()
                lines = Lines.objects.all()

            station = None  # Not tied to one station
        else:
            # Operator — only equipment in their station
            station = request.user.station
            equipments = Equipment.objects.filter(station=station)
            lines = Lines.objects.filter(station=station)

        context = {
            "user": request.user,
            "station": station,
            "equipments": equipments,
            "lines": lines,
        }
    station = request.user.station
    # equipments = Equipment.objects.filter(station=station).all()
    # lines = Lines.objects.filter(station=station).all()
    # context = {"user": request.user, "station": station, "equipments": equipments, "lines": lines}
    
    if request.method == "POST":
        username = request.user  # Assuming user is logged in
        station = request.user.station
        protection_gurantee = request.POST.get("pg")
        equipment_id = request.POST.get("equipment")
        line_id = request.POST.get("line")
        work_description = request.POST.get("work")
        load_involved = request.POST.get("load")
        apparatus = request.POST.get("apparatus")
        outage_type = request.POST.get("outage_type")
        
        start_date = request.POST.get("start_date")
        start_time = request.POST.get("start_time")
        end_date = request.POST.get("end_date")
        end_time = request.POST.get("end_time")
        
        reason_sub = request.POST.get("reason_sub")
        reason_others = request.POST.get("other_reason")
        
        remark = request.POST.get("remark")
        
        areas_affected = request.POST.get("areas_affected", "").strip()
        notification_text = request.POST.get("notified", "").strip()
        date_notified = request.POST.get("date_notified")
        time_notified = request.POST.get("time_notified")
        
        # Call validation function
        errors = validate_request_data(start_date, start_time, end_date, end_time, equipment_id, line_id, work_description, date_notified, time_notified)
        
        # If errors exist, show messages and return
        if errors:
            for error in errors:
                messages.error(request, error)
                context.update({"form_data": request.POST})
            return render(request, "requests/add_request.html", context)
            #return redirect("add_request")
        
        # Convert times to 24-hour format (Django automatically stores in 24-hour format)
        try:
            start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            messages.error(request, "Invalid time format. Please use HH:MM format.")
            context.update({"form_data": request.POST})
            return render(request, "requests/add_request.html", context)
            #return redirect("add_request")
        
        # Validate start_date & start_time are not greater than end_date & end_time
        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
        
        if start_datetime >= end_datetime:
            messages.error(request, "Start date and time must be before end date and time.")
            context.update({"form_data": request.POST})
            return render(request, "requests/add_request.html", context)
            #return redirect("add_request")
        
        # If notification text is empty, ignore date_notified & time_notified
        if not notification_text:
            date_notified = None
            time_notified = None
        else:
            try:
                time_notified = datetime.strptime(time_notified, "%H:%M").time() if time_notified else None
            except ValueError:
                messages.error(request, "Invalid time format for notification.")
                context.update({"form_data": request.POST})
                return render(request, "requests/add_request.html", context)
                #return redirect("add_request")
        
        equipment = Equipment.objects.filter(id=equipment_id).first() if equipment_id else None
        line = Lines.objects.filter(id=line_id).first() if line_id else None
        notified_text = f"{notification_text} At {time_notified}HRS {date_notified}"
        
        # Additional validations for planned outages
        if outage_type:
            outage_type = outage_type.lower()

            if outage_type == "planned":
                selected_item = equipment if equipment is not None else line
                if not selected_item:
                    messages.error(request, "Please select either an equipment or a line for a planned outage.")
                    context.update({"form_data": request.POST})
                    return render(request, "requests/add_request.html", context)
                    #return redirect("add_request")
                
                from django.utils import timezone
                application_date = timezone.now().date()
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()

                if (start_date_obj - application_date).days < 14:
                    messages.error(
                        request,
                        "YOUR APPLICATION DOES NOT MEET THE REQUIRED TWO WEEKS NOTICE... PLEASE CHANGE YOUR OUTAGE TO URGENT FOR A SUCCESSFUL APPLICATION"
                    )
                    context.update({"form_data": request.POST})
                    return render(request, "requests/add_request.html", context)
                    #return redirect("add_request")

            elif outage_type == "annual":
                selected_item = equipment if equipment is not None else line
                if not selected_item:
                    messages.error(request, "Please select either an equipment or a line for annual maintenance.")
                    context.update({"form_data": request.POST})
                    return render(request, "requests/add_request.html", context)
                    #return redirect("add_request")
                
                approved_date = selected_item.approve_date
                if not approved_date:
                    messages.error(request, "The selected equipment/line does not have an approved date. Kindly Contact a NCC Staff")
                    context.update({"form_data": request.POST})
                    return render(request, "requests/add_request.html", context)
                    #return redirect("add_request")
                
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()

                # 1. Check that start_date == approved_date
                if start_date_obj != approved_date and reason_sub == "":
                    
                    if reason_sub == "others" and reason_others == "":
                        messages.error(request, "THE REQUESTED DATE DOES NOT MATCH THE SCHEDULED DATE FOR ANNUAL MAINTENANCE. KINDLY PROVIDE THE REASON")
                        context.update({"form_data": request.POST})
                        return render(request, "requests/add_request.html", context)                    
                    
                    messages.error(request, "THE REQUESTED DATE DOES NOT MATCH THE SCHEDULED DATE FOR ANNUAL MAINTENANCE. KINDLY PROVIDE THE REASON")
                    context.update({"form_data": request.POST})
                    return render(request, "requests/add_request.html", context)
                    #return redirect("add_request")

                # 2. (Optional) Check 14 days only if admin enabled                
                if selected_item.check_14_days:
                    from django.utils import timezone
                    application_date = timezone.now().date()

                    if (approved_date - application_date).days < 14 and reason_sub == "":
                        messages.error(
                            request,
                            "ANNUAL MAINTENANCE MUST BE REQUESTED WITH AT LEAST TWO WEEKS NOTICE. KINDLY PROVIDE THE REASON"
                        )
                        context.update({"form_data": request.POST})
                        return render(request, "requests/add_request.html", context)
                        #return redirect("add_request")
                
                if reason_sub == "others" and reason_others != "":
                    reason_sub = reason_others
        
        #Check for notification of stalkholder 
        if float(load_involved) >= 0.1 and notification_text == "":
            messages.error(
                            request,
                            "APPROPRIATE STALKHOLDER SHOULD BE DULY NOTIFIED"
                        )
            context.update({"form_data": request.POST})
            return render(request, "requests/add_request.html", context)
        
        # Create the new request
        new_request = Request.objects.create(
            user=username,
            station=station,
            protection_gurantee=protection_gurantee,
            equipment=equipment,
            line=line,
            work_description=work_description,
            load_involved=load_involved,
            apparatus_for_safe_working_space=apparatus,
            outage_type=outage_type,
            start_date=start_date,
            start_time=start_time_obj,  # Stored in 24H format
            end_date=end_date,
            end_time=end_time_obj,      # Stored in 24H format
            reason_submission_issues = reason_sub,
            area_affected=areas_affected,
            disco_genco_notified=notified_text,
            remarks=remark            
        )
        new_request.save()
        
        log_request_action(
            request_obj=new_request,
            user=request.user,
            action='created_request',
            message=f"Request created with ID {new_request.request_id} by {request.user.username}"
        )
        
        messages.success(request, "Request successfully created!")
        return redirect("all_requests")
    
    return render(request, "requests/add_request.html", context)

@login_required
def edit_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)

    # Only Admins, Reviewers, or the same user can edit
    if not (request.user.is_admin or request.user.is_reviewer or req.user == request.user):
        messages.error(request, "You are not authorized to edit this request.")
        return redirect("all_requests")

    # Same equipment/line filtering logic as create_request
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_reviewer or request.user.is_approver:
            # Admins, Approvers, Reviewers
            if request.user.is_reviewer:
                # Reviewer — only for equipment in user's region
                user_region = request.user.region
                equipments = Equipment.objects.filter(station__region=user_region)
                lines = Lines.objects.filter(station__region=user_region)
            else:
                # Admin or Approver — full access
                equipments = Equipment.objects.all()
                lines = Lines.objects.all()

            station = None  # Not tied to one station
        else:
            # Operator — only equipment in their station
            station = request.user.station
            equipments = Equipment.objects.filter(station=station)
            lines = Lines.objects.filter(station=station)

    context = {
        "user": request.user,
        "equipments": equipments,
        "lines": lines,
        "req": req,  # Pass the request object for pre-populating form
    }

    if request.method == "POST":
        protection_gurantee = request.POST.get("pg")
        equipment_id = request.POST.get("equipment")
        line_id = request.POST.get("line")
        work_description = request.POST.get("work")
        load_involved = request.POST.get("load")
        apparatus = request.POST.get("apparatus")
        outage_type = request.POST.get("outage_type")
        start_date = request.POST.get("start_date")
        start_time = request.POST.get("start_time")
        end_date = request.POST.get("end_date")
        end_time = request.POST.get("end_time")
        reason_sub = request.POST.get("reason_sub")
        reason_others = request.POST.get("other_reason")
        remark = request.POST.get("remark")
        areas_affected = request.POST.get("areas_affected", "").strip()
        notification_text = request.POST.get("notified", "").strip()
        date_notified = request.POST.get("date_notified")
        time_notified = request.POST.get("time_notified")

        # Run your same validations (reuse validate_request_data)
        errors = validate_request_data(start_date, start_time, end_date, end_time, equipment_id, line_id, work_description)
        if errors:
            for error in errors:
                messages.error(request, error)
            context.update({"form_data": request.POST})
            return render(request, "requests/edit_request.html", context)

        # Update object
        req.protection_gurantee = protection_gurantee
        req.equipment = Equipment.objects.filter(id=equipment_id).first() if equipment_id else None
        req.line = Lines.objects.filter(id=line_id).first() if line_id else None
        req.work_description = work_description
        req.load_involved = load_involved
        req.apparatus_for_safe_working_space = apparatus
        req.outage_type = outage_type
        req.start_date = start_date
        req.start_time = datetime.strptime(start_time, "%H:%M").time()
        req.end_date = end_date
        req.end_time = datetime.strptime(end_time, "%H:%M").time()
        req.reason_submission_issues = reason_sub if reason_sub != "others" else reason_others
        req.area_affected = areas_affected
        req.disco_genco_notified = notification_text
        req.remarks = remark
        req.save()

        log_request_action(
            request_obj=req,
            user=request.user,
            action='edited_request',
            message=f"Request ID {req.request_id} updated by {request.user.username}"
        )

        messages.success(request, "Request successfully updated!")
        return redirect("all_requests")

    return render(request, "requests/edit_request.html", context)


@login_required
def view_request(request, request_id):
    request_form = get_object_or_404(Request, id=request_id)
    print(request_form.seen_by_approval)
    context = {"req" : request_form}    
    
    return render(request, "requests/view_request.html", context)

@login_required
def review_request(request, request_id):
    request_form = get_object_or_404(Request, id=request_id)
    context = {"req" : request_form}
    return render(request, "requests/review_request.html", context)

@login_required
def review_request_post(request, request_id):
    request_form = get_object_or_404(Request, id=request_id)
    if request.method == "POST":
        request_form.reviewed_by = request.user
        request_form.reviewer_comment = request.POST.get("comment")
        request_form.is_reviewed = True
        request_form.is_satisfied = request.POST.get("review") == "on"
        request_form.reviewed_at = timezone.now()
        
        if not request_form.reviewer_comment:
            messages.error(request, "Comment is required.")
            return redirect("review_request", request_id=request_id)
        
        request_form.save()
        log_request_action(
            request_obj=request_form,
            user=request.user,
            action='reviewed_request',
            message=f"Reviewed: {request_form.reviewer_comment} by {request.user.username}"
        )
        
        return redirect("view_request", request_id=request_id)
        
        
    return redirect("view_request", request_id=request_id)

@login_required
def approve_request(request, request_id):
    request_form = get_object_or_404(Request, id=request_id)
    
    if not request_form.is_reviewed:
        messages.error(request, "Request needs to be reviewed.")
        redirect("view_request", request_id=request_id)
        
    context = {"req" : request_form}
    return render(request, "requests/approve_request.html", context)

@login_required
def approve_request_post(request, request_id):
    request_form = get_object_or_404(Request, id=request_id)
    
    if request.method == "POST":
        request_form.seen_by_approval = True
        request_form.approve_by = request.user
        request_form.approved_comment = request.POST.get("comment")
        is_approved = request.POST.get("approve") == "on"
        request_form.is_approved = is_approved
        request_form.approved_at = timezone.now()
        
        if not request_form.approved_comment:
            messages.error(request, "Comment is required.")
            return redirect("approve_request", request_id=request_id)
        
        # --- NEW: increment nota or dota atomically ---
        if is_approved:
            # increment nota
            #Request.objects.filter(pk=request_form.pk).update(nota=F('nota') + 1)
            request_form.nota = request_form.nota + 1
        else:
            # increment dota
            #Request.objects.filter(pk=request_form.pk).update(dota=F('dota') + 1)
            request_form.dota = request_form.dota + 1
        
        # reload the updated counts
        #request_form.refresh_from_db()
        
        request_form.save()
        
        log_request_action(
            request_obj=request_form,
            user=request.user,
            action='approved_request',
            message=f"{'Approved' if is_approved else 'Disapproved'} with comment {request_form.approved_comment} by {request.user.username}"
        )
        
        return redirect("view_request", request_id=request_id)
        
        
    return redirect("view_request", request_id=request_id)

@login_required
def confirm_execution(request, request_id):
    req = get_object_or_404(Request, id=request_id)

    # Optional: permission check
    # if not request.user.is_operator:
    #     messages.error(request, "You don't have permission.")
    #     return redirect('view_request', request_id)

    if request.method == 'POST':
        executed = request.POST.get('executed') == 'on'
        comment = request.POST.get('execution_comment', '').strip()

        if executed and not comment:
            messages.error(request, 'Please provide a comment when confirming execution.')
            return render(request, 'requests/confirm_execution.html', {'req': req})
        
        if not comment:
            messages.error(request, 'Please provide a comment')
            return render(request, 'requests/confirm_execution.html', {'req': req})

        # Update fields
        req.is_executed = executed
        req.execution_comment = comment
        req.executed_by = request.user #if executed else None
        req.executed_at = timezone.now() #if executed else None
        req.save()

        # Log action
        action = 'executed_request' if executed else 'mark_not_executed'
        message = f"Executed: {comment}" if executed else "Marked as not executed"
        log_request_action(
            request_obj=req,
            user=request.user,
            action=action,
            message=message
        )

        messages.success(request, 'Execution status updated.')
        return redirect('view_request', request_id)

    # GET: show confirmation form
    return render(request, 'requests/confirm_execution.html', {'req': req})

@login_required
def generate_request_report(request, request_id):
    req = Request.objects.get(id=request_id)  # Fetch request data

    # Render template to HTML
    html_string = render(request, 'request_report.html', {'request': req}).content.decode('utf-8')

    # Convert HTML to PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # Create response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Request_Report_{req.id}.pdf"'

    return response

@login_required
def all_reviewed_requests(request):
    # requests = Request.objects.all()
    # Get all requests sorted from latest to oldest
    requests = Request.objects.all().order_by("-created_at").filter(is_reviewed=True)
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
    
    # if not request.user.is_admin or not request.user.is_reviewer or not request.user.is_approver:
    #     requests = requests.filter(station=request.user.station)
    # Restricting operators to only see their station's requests
    if not (request.user.is_admin or request.user.is_reviewer or request.user.is_approver):
        requests = requests.filter(station=request.user.station)
        
    context = {
        "requests": requests,        
        "regions": regions,
        "accs": accs,
        "stations": stations,
    }
    
    return render(request, "requests/all_reviewed_request.html", context)

@login_required
def all_approved_requests(request):
    # requests = Request.objects.all()
    # Get all requests sorted from latest to oldest
    requests = Request.objects.all().order_by("-created_at").filter(is_approved=True)
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
    
    # if not request.user.is_admin or not request.user.is_reviewer or not request.user.is_approver:
    #     requests = requests.filter(station=request.user.station)
    # Restricting operators to only see their station's requests
    if not (request.user.is_admin or request.user.is_reviewer or request.user.is_approver):
        requests = requests.filter(station=request.user.station)
        
    context = {
        "requests": requests,        
        "regions": regions,
        "accs": accs,
        "stations": stations,
    }
    
    return render(request, "requests/all_approved_request.html", context)

# @login_required
# def edit_request(request, request_id):
#     req = get_object_or_404(Request, id=request_id)

#     # Only allow certain users (optional):
#     # if not (request.user.is_admin or request.user == req.user):
#     #     messages.error(request, "You don't have permission to edit this request.")
#     #     return redirect('view_request', request_id=request_id)

#     if request.method == 'POST':
#         outage_type = request.POST.get('outage_type')
#         work_description = request.POST.get('work')

#         errors = []
#         if not outage_type:
#             errors.append("Outage type is required.")
#         if not work_description or not work_description.strip():
#             errors.append("Work description cannot be empty.")

#         if errors:
#             for err in errors:
#                 messages.error(request, err)
#             # re-render form with previous input
#             context = {'req': req}
#             return render(request, 'requests/edit_request.html', context)

#         # Update model
#         req.outage_type = outage_type
#         req.work_description = work_description
#         req.save()

#         # Log the edit action
#         log_request_action(
#             request_obj=req,
#             user=request.user,
#             action='edited_request',
#             message=f"Outage type set to '{outage_type}', work-description updated"
#         )

#         messages.success(request, 'Request updated successfully!')
#         return redirect('view_request', request_id=req.id)

#     # GET: show form
#     context = {'req': req}
#     return render(request, 'requests/edit_request.html', context)



def activity_logs(request):
    """
    Display the latest 150 log entries in a modal or standalone page.
    """
    # logs = RequestLog.objects.select_related('request', 'user').order_by('-timestamp')[:150]
    logs = RequestLog.objects.all()  # Start fresh
    req_id = request.GET.get('request_id')
    
    if req_id:
        logs = logs.filter(request__request_id=req_id)
    
    logs = logs.order_by('-timestamp')[:150]        
    context = {'logs': logs}
    return render(request, 'requests/logs_modal.html', context)

def validate_request_data(start_date, start_time, end_date, end_time, equipment_id, line_id, work_description, date_notified, time_notified):
    errors = []

    # Check if date and time fields are filled
    if not start_date or not start_time or not end_date or not end_time:
        errors.append("START DATE, START TIME, END DATE, AND END TIME ARE REQUIRED.")

    # Ensure at least one of equipment or line is selected
    if not equipment_id and not line_id:
        errors.append("AT LEAST ONE OF EQUIPMENT OR LINE MUST BE SELECTED.")

    # Ensure work description is not empty
    if not work_description.strip():
        errors.append("WORK DESCRIPTION IS REQUIRED.")

    # Ensure Notification of Stalkholder is not in the future
    if date_notified and time_notified:
            # Convert strings to datetime
            notified_dt = datetime.strptime(
                f"{date_notified} {time_notified}", "%Y-%m-%d %H:%M"
            )

            # Make timezone-aware
            notified_dt = timezone.make_aware(notified_dt, timezone.get_current_timezone())

            # Check if it's in the future
            if notified_dt > timezone.now():
                errors.append("NOTIFICATION DATETIME CANNOT BE IN THE FUTURE.")


    return errors

@require_GET
def get_approved_date(request):
    item_id = request.GET.get("item_id")
    item_type = request.GET.get("item_type")
    if not item_id:
        return JsonResponse({"error": "Missing item_id"}, status=400)

    try:
        day_format = "%#d" if platform.system() == "Windows" else "%-d"
        if item_type == "equipment":
            item = Equipment.objects.get(id=item_id)   
            # ✅ Check if approved_date is None
            if not item.approve_date:
                return JsonResponse({"approved_date": "No Date"})         
            formatted_date = item.approve_date.strftime(f"%a, {day_format} %B, %Y")            
            return JsonResponse({"approved_date": formatted_date})
        
        if item_type == "line":
            item = Lines.objects.get(id=item_id)
            # ✅ Check if approved_date is None
            if not item.approve_date:
                return JsonResponse({"approved_date": "No Date"})         
            formatted_date = item.approve_date.strftime(f"%a, {day_format} %B, %Y")            
            return JsonResponse({"approved_date": formatted_date})
        
        return JsonResponse({"approved_date": None})
    except Equipment.DoesNotExist:
        return JsonResponse({"approved_date": None})
    except Lines.DoesNotExist:
        return JsonResponse({"approved_date": None})