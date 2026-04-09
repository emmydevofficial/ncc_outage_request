from django.db import models
from stations.models import Station
from equipment.models import Lines, Equipment
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# Create your models here.
class Request(models.Model):
    request_id = models.CharField(max_length=40, unique=True, editable=False, null=False,
        help_text="Custom request identifier like REQ-00001 or REQ-<UUID>"
    )
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests") 
    protection_gurantee = models.CharField( max_length=50)
    outage_type = models.CharField(max_length=64, null=True)
    start_date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_date = models.DateField(null=True)
    end_time = models.TimeField(null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.DO_NOTHING, blank=True, null=True)
    line = models.ForeignKey(Lines, on_delete=models.DO_NOTHING, blank=True, null=True)
    custom_equipment_name = models.CharField(max_length=255, blank=True, null=True)
    custom_line_name = models.CharField(max_length=255, blank=True, null=True)
    work_description = models.TextField()
    load_involved = models.CharField( max_length=50)
    area_affected = models.TextField(null=True)
    disco_genco_notified = models.TextField(null=True)
    reason_submission_issues = models.TextField(null=True) 
    is_reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null= True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="reviewed_requests", null=True, blank=True)  # Reviewer
    reviewer_comment = models.TextField(null=True, blank=True)
    approve_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="approved_requests", null=True, blank=True)  # Reviewer
    seen_by_approval = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_comment = models.TextField(null=True, blank=True)
    apparatus_for_safe_working_space = models.CharField( max_length=512, blank=True)
    nota = models.IntegerField(default=0, help_text="Number of times approved")
    dota = models.IntegerField(default=0, help_text="Number of times disapproved")
    is_executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)
    executed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executed_requests'
    )
    execution_comment = models.TextField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField( auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate request_id on first save
        if not self.request_id:
            # Option 1: Sequential numeric ID
            #last = Request.objects.order_by('-id').first()
            #next_id = last.id + 1 if last else 1
            #self.request_id = f"REQ-{next_id:05d}"
            # Option 2: UUID
            self.request_id = f"REQ-{uuid.uuid4().hex.upper()[:8]}"  # Short UUID
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"""Request by {self.user.first_name} in {self.station.name} for {self.work_description}"""
    
    
class RequestLog(models.Model):
    """
    Logs actions performed on a Request.
    """
    log_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique log entry ID"
    )
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    message = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp.isoformat()} - {self.action}"

    
    