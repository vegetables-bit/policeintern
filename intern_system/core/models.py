from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

class UserProfile(models.Model):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('police', 'Police Supervisor'),
        ('school', 'School Supervisor'),
        ('intern', 'Intern'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username
    
class AdminProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=200)

    position = models.CharField(
        max_length=200,
        default='System Administrator'
    )

    department = models.CharField(
        max_length=100,
        default='Other'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class AdminSettingsProfile(models.Model):
    """Additional settings/profile data for Admin accounts.

    Kept separate from AdminProfile to avoid breaking existing logic/templates.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_settings_profile',
    )

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=30, blank=True, default='')

    profile_picture = models.ImageField(
        upload_to='admin_profile_pictures/',
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"


class SystemInformation(models.Model):
    """Stores system-wide information shown on Settings page."""

    # Single-row pattern: always keep ID=1 in production.
    # (We still allow admin to create it if missing.)
    system_name = models.CharField(max_length=200, default='Police Intern Tracking System')
    organization_name = models.CharField(max_length=200, default='Police Headquarters')
    contact_email = models.EmailField(blank=True, default='')
    contact_phone_number = models.CharField(max_length=30, blank=True, default='')

    system_logo = models.ImageField(
        upload_to='system_logos/',
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.system_name

    
# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# School Supervisor (HOD)
class SchoolSupervisor(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=150)

    full_name = models.CharField(max_length=100)

    institution_name = models.CharField(max_length=150)

    employee_id = models.CharField(max_length=50)

    department = models.CharField(max_length=100)

    position = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

# Police Supervisor
class PoliceSupervisor(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    police_id = models.CharField(
        max_length=50
    )

    rank = models.CharField(
        max_length=50
    )

    department = models.CharField(
        max_length=100
    )

    station = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField()

    is_approved = models.BooleanField(
        default=True
    )

    def __str__(self):

        return self.full_name

# Intern Model
class Intern(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    full_name = models.CharField(max_length=150)

    gender = models.CharField(max_length=10)

    age = models.IntegerField(
        blank=True,
        null=True
    )

    blood_group = models.CharField(max_length=5)

    marital_status = models.CharField(max_length=10)

    phone = models.CharField(max_length=15)

    email = models.EmailField()

    address = models.TextField()

    institution = models.CharField(max_length=150)

    program = models.CharField(max_length=150)

    start_date = models.DateField(
        null=True,
        blank=True
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

    # Internship monitoring values are the single source of truth for the
    # police dashboard, intern dashboard, and weekly PDF report.

    attendance_percentage = models.IntegerField(
        default=0
    )

    performance_score = models.IntegerField(
        default=0
    )

    working_days = models.IntegerField(
        default=0
    )

    present_days = models.IntegerField(
        default=0
    )

    late_days = models.IntegerField(
        default=0
    )

    absent_days = models.IntegerField(
        default=0
    )

    total_hours = models.IntegerField(
        default=0
    )

    activities_done = models.TextField(
        blank=True,
        null=True
    )

    warning_message = models.TextField(
        blank=True,
        null=True
    )

    appreciation_message = models.TextField(
        blank=True,
        null=True
    )

    last_updated = models.DateTimeField(
        auto_now=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_approved = models.BooleanField(
        default=False
    )

    # Supervisors

    school_supervisor = models.ForeignKey(
        SchoolSupervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    police_supervisor = models.ForeignKey(
        PoliceSupervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if self.attendance_percentage < 60 or self.performance_score < 50:
            self.warning_message = (
                'Intern performance and/or attendance are below expected standards. '
                'Please improve attendance, productivity, and task completion.'
            )
        else:
            self.warning_message = ''

        if self.performance_score >= 80 and self.attendance_percentage >= 80:
            self.appreciation_message = (
                'Excellent performance and attendance. Keep up the great work!'
            )
        else:
            self.appreciation_message = ''

        super().save(*args, **kwargs)

    @property
    def latest_application(self):
        # Prefer applications explicitly linked to this Intern.
        return self.applications.order_by('-submitted_at').first()

    @property
    def has_submitted_application(self):
        return self.applications.exists()

    @property
    def application_status(self):
        latest = self.latest_application
        return latest.status if latest else None

    @property
    def is_dashboard_approved(self):
        return self.is_approved or self.is_application_approved

    @property
    def has_assigned_supervisors(self):
        return bool(self.police_supervisor or self.school_supervisor)

    # Helper accessors expected by the business rules
    @property
    def has_application(self):
        return self.applications.exists()

    @property
    def is_application_approved(self):
        # If any linked application is approved, consider the application approved
        return self.applications.filter(status='Approved').exists()

    @property
    def assigned_police_supervisor(self):
        return self.police_supervisor

    @property
    def assigned_school_supervisor(self):
        return self.school_supervisor

    @property
    def can_view_messages(self):
        return self.is_dashboard_approved

    @property
    def can_view_performance(self):
        return self.is_dashboard_approved

    @property
    def application_notification(self):
        if self.is_dashboard_approved:
            return 'Your application has been approved.'
        if not self.has_submitted_application:
            return 'No notifications yet.'
        if self.application_status == 'Pending':
            return 'Your internship application is under review.'
        if self.application_status == 'Rejected':
            return 'Your application has been rejected.'
        return 'No notifications yet.'

    @property
    def total_hours_worked(self):
        return self.total_hours

    @property
    def overall_weekly_rating(self):
        average_score = (self.performance_score + self.attendance_percentage) / 2
        if average_score >= 85:
            return 'Excellent'
        if average_score >= 70:
            return 'Very Good'
        if average_score >= 50:
            return 'Good'
        if average_score >= 40:
            return 'Satisfactory'
        return 'Needs Improvement'

    @property
    def police_supervisor_signature(self):
        if self.police_supervisor:
            return self.police_supervisor.full_name
        return ''

    def __str__(self):
        return self.full_name


# Comments Model
class Comment(models.Model):
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_type = models.CharField(max_length=20)  # Police or School
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.intern.full_name} - {self.comment_type}"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class StudentApplication(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    )

    # Link application to an Intern when available to avoid ambiguous
    # email-based lookups and ensure ownership.
    intern = models.ForeignKey(
        'Intern',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications'
    )

    photo = models.ImageField(
        upload_to='applications/',
        null=True,
        blank=True
    )

    full_name = models.CharField(max_length=200)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')

    date_of_birth = models.DateField()

    reg_number = models.CharField(max_length=100)

    school_name = models.CharField(max_length=200)

    program = models.CharField(max_length=200)

    semester = models.CharField(max_length=100)

    year = models.CharField(max_length=100)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    email = models.EmailField()

    phone_number = models.CharField(max_length=20)

    school_id = models.FileField(
        upload_to='documents/'
    )

    national_id = models.FileField(
        upload_to='documents/'
    )

    recommendation_letter = models.FileField(
        upload_to='documents/'
    )

    transcript = models.FileField(
        upload_to='documents/'
    )

    application_letter = models.FileField(
        upload_to='documents/'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
class WeeklyReport(models.Model):

    intern = models.ForeignKey(
        Intern,
        on_delete=models.CASCADE
    )

    week_start = models.DateField()

    week_end = models.DateField()

    generated_at = models.DateTimeField(
        auto_now_add=True
    )

    pdf_file = models.FileField(
        upload_to='weekly_reports/',
        null=True,
        blank=True
    )

    overall_rating = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    police_remark = models.TextField(
        blank=True,
        null=True
    )

    school_remark = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):

        return f"{self.intern.full_name} Report"
    

class Message(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )

    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )

    receiver = models.ForeignKey(
        User,
        related_name='received_messages',
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=255)

    message_body = models.TextField()

    sent_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')

    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.subject} - from {self.sender.username} to {self.receiver.username}"
