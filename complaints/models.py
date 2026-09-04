from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = [
        ("student", "Student/User"),
        ("admin", "Admin"),
        ("staff", "Service Staff"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="student"
    )

    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Complaint(models.Model):
    """The core model - every submitted complaint, typed or voice, becomes
    one row here."""

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]

    PRIORITY_CHOICES = [
        ("HIGH", "High"),
        ("MEDIUM", "Medium"),
        ("LOW", "Low"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)

    # These two get auto-filled by your classifier, not typed by the user
    category = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    image = models.ImageField(upload_to="complaint_images/", blank=True, null=True)

    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints_submitted")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="complaints_assigned")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    resolution_remarks = models.TextField(
    blank=True,
    null=True
)
    
    def __str__(self):
        return f"{self.title} [{self.priority}]"

    def save(self, *args, **kwargs):
        """Auto-run the classifier whenever a complaint is created,
        so category/priority are filled in without the user picking them."""
        if not self.category:  # only classify on first save, not every edit
            from .priority_utils import classify_complaint
            result = classify_complaint(self.description)
            self.category = result["category"]
            self.priority = result["priority"]
        super().save(*args, **kwargs)


# Add this at the very bottom of complaints/models.py

class Comment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.complaint.title}"