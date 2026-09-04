from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Complaint

@receiver(pre_save, sender=Complaint)
def send_complaint_status_email(sender, instance, **kwargs):
    # If the complaint is brand new and hasn't been saved to DB yet, skip.
    if not instance.pk:
        return
        
    try:
        # Get the old version of the complaint from the database
        old_instance = Complaint.objects.get(pk=instance.pk)
    except Complaint.DoesNotExist:
        return
        
    # Check if the status has actually changed
    if old_instance.status != instance.status:
        
        # Get the email of the student who submitted it
        student_email = instance.submitted_by.email
        
        # If the student didn't provide an email, we can't send anything
        if not student_email:
            return
            
        subject = ''
        message = ''
        
        # 1. If assigned to staff
        if instance.status == 'assigned':
            staff_name = instance.assigned_to.username if instance.assigned_to else "Staff"
            subject = f'Update: Your issue "{instance.title}" has been assigned'
            message = f'Hello {instance.submitted_by.username},\n\nYour complaint regarding "{instance.title}" has been assigned to our staff member, {staff_name}. Work will begin shortly.\n\nThank you,\nSmart Complaint System'
            
        # 2. If resolved
        elif instance.status == 'resolved':
            subject = f'Resolved: Your issue "{instance.title}"'
            remarks = instance.resolution_remarks if instance.resolution_remarks else "No specific remarks provided."
            message = f'Hello {instance.submitted_by.username},\n\nGood news! Your complaint "{instance.title}" has been resolved.\n\nResolution Remarks:\n{remarks}\n\nThank you,\nSmart Complaint System'
            
        # Send the email if we have a subject and message
        if subject and message:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [student_email],
                fail_silently=False,
            )