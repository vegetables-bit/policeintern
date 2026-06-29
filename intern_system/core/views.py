import json
import os
from datetime import date, datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .forms import (
    AdminRegistrationForm,
    CommentForm,
    InternForm,
    InternUpdateForm,
    PoliceSupervisorForm,
    SchoolSupervisorForm,
    StudentApplicationForm,
    SystemInformationForm,
    AdminSettingsProfileForm,
    AdminChangePasswordForm,
    MessageForm,
)


from .models import (
    AdminProfile,
    AdminSettingsProfile,
    Comment,
    Department,
    Intern,
    PoliceSupervisor,
    SchoolSupervisor,
    StudentApplication,
    SystemInformation,
    UserProfile,
    WeeklyReport,
    Message,
)

from reportlab.lib.utils import ImageReader

def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            try:

                profile = user.userprofile

            except UserProfile.DoesNotExist:

                return render(
                    request,
                    'core/login.html',
                    {
                        'error':
                        'User profile not found.'
                    }
                )

            # ADMIN
            if role == 'admin' and profile.role == 'admin':

                return redirect('admin_dashboard')

            # POLICE SUPERVISOR
            elif role == 'police' and profile.role == 'police':

                return redirect('police_dashboard')

            # SCHOOL SUPERVISOR
            elif role == 'school' and profile.role == 'school':

                return redirect('school_dashboard')

            # INTERN
            elif role == 'intern' and profile.role == 'intern':

                return redirect('intern_dashboard')

            else:

                return render(
                    request,
                    'core/login.html',
                    {
                        'error':
                        'Invalid role selected for this account.'
                    }
                )

        else:

            return render(
                request,
                'core/login.html',
                {
                    'error':
                    'Invalid username or password.'
                }
            )

    return render(
        request,
        'core/login.html'
    )

def is_ict_admin(user):
    try:
        return (
            user.userprofile.role == 'admin' and
            user.adminprofile.department.strip().upper() == 'ICT'
        )
    except Exception:
        return False


def admin_dashboard(request):

    interns = Intern.objects.all()

    total_interns = interns.count()

    total_departments = Department.objects.count()

    total_comments = Comment.objects.count()

    # Chart data comes from the same Intern fields updated by InternUpdateForm.
    intern_names = []
    attendance_data = []
    performance_data = []

    for intern in interns:

        intern_names.append(intern.full_name)

        attendance_data.append(intern.attendance_percentage)

        performance_data.append(intern.performance_score)

    context = {

        'total_interns': total_interns,
        'total_departments': total_departments,
        'total_comments': total_comments,

        'intern_names': json.dumps(intern_names),
        'attendance_data': json.dumps(attendance_data),
        'performance_data': json.dumps(performance_data),

    }

    return render(
        request,
        'core/admin_dashboard.html',
        context
    )

@login_required
def add_admin(request):

    # Only ICT admins can add new admins
    if not is_ict_admin(request.user):
        return redirect('manage_users')

    if request.method == 'POST':

        form = AdminRegistrationForm(request.POST)

        if form.is_valid():

            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email']
            )
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile, created = UserProfile.objects.get_or_create(
                user=user
            )
            profile.role = 'admin'
            profile.save()

            admin = form.save(commit=False)
            admin.user = user
            admin.save()

            messages.success(
                request,
                'Administrator account created successfully.'
            )

            return redirect('view_admins')

        messages.error(request, 'Please correct the errors below and try again.')

    else:

        form = AdminRegistrationForm()

    return render(
        request,
        'core/add_admin.html',
        {'form': form}
    )
    
@login_required
@login_required
def view_admins(request):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    admins = AdminProfile.objects.all()

    return render(
        request,
        'core/view_admins.html',
        {'admins': admins}
    )

def register_school(request):

    if request.method == 'POST':

        form = SchoolSupervisorForm(request.POST)

        if form.is_valid():

            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email']
            )
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile, created = UserProfile.objects.get_or_create(
                user=user
            )
            profile.role = 'school'
            profile.save()

            supervisor = form.save(commit=False)
            supervisor.user = user
            supervisor.is_approved = False
            supervisor.save()
            
            messages.success(
                request,
                'School Supervisor account created successfully.'
            )

            return redirect('account_pending')

        messages.error(request, 'Please correct the errors below and try again.')

    else:

        form = SchoolSupervisorForm()

    return render(request,
                  'core/register_school.html',
                  {'form': form})

# =========================================
# LANDING PAGE
# =========================================

def home(request):
    return render(request, 'core/home.html')


# =========================================
# LOGIN REDIRECTION
# =========================================

def redirect_user(user):

    try:
        role = user.userprofile.role
    except:
        return redirect('login')

    if UserProfile.role == 'admin':
        return redirect('admin_dashboard')

    elif UserProfile.role == 'police':
        return redirect('police_dashboard')

    elif UserProfile.role == 'school':
        return redirect('school_dashboard')
    
    elif UserProfile.role == 'intern':
        return redirect('intern_dashboard')

    else:
        return redirect('login')


# =========================================
# LOGIN
# =========================================

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').strip()

        if not username or not password or not role:
            return render(
                request,
                'core/login.html',
                {
                    'error': 'All fields are required.',
                    'selected_role': role,
                    'username': username
                }
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            profile = UserProfile.objects.filter(user=user).first()

            if not profile:
                return render(
                    request,
                    'core/login.html',
                    {'error': 'No profile found.'}
                )

            if profile.role != role:
                return render(
                    request,
                    'core/login.html',
                    {
                        'error': 'Selected role does not match this account.',
                        'selected_role': role,
                        'username': username
                    }
                )

            login(request, user)

            if profile.role == 'admin':
                return redirect('admin_dashboard')

            elif profile.role == 'police':
                return redirect('police_dashboard')

            elif profile.role == 'intern':
                return redirect('intern_dashboard')

            elif profile.role == 'school':
                supervisor = SchoolSupervisor.objects.filter(
                    user=user
                ).first()

                if supervisor and not supervisor.is_approved:
                    return render(
                        request,
                        'core/login.html',
                        {
                            'error': 'Your account is pending admin approval.',
                            'selected_role': role,
                            'username': username
                        }
                    )

                return redirect('school_dashboard')

            return render(
                request,
                'core/login.html',
                {'error': 'Invalid user role selected.'}
            )

        return render(
            request,
            'core/login.html',
            {'error': 'Invalid username or password.', 'selected_role': role, 'username': username}
        )

    return render(request, 'core/login.html')

# =========================================
# LOGOUT
# =========================================

def user_logout(request):
    logout(request)
    return redirect('login')


# =========================================
# ADMIN DASHBOARD
# =========================================

@login_required
def admin_dashboard(request):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    total_interns = Intern.objects.count()

    total_departments = Department.objects.count()

    total_comments = Comment.objects.count()

    # GET ALL INTERNS
    interns = Intern.objects.all()

    attendance_data = []

    performance_data = []

    intern_names = []

    for intern in interns:

        attendance_data.append(intern.attendance_percentage)

        performance_data.append(intern.performance_score)

        intern_names.append(intern.full_name)

    # PENDING SCHOOL SUPERVISORS
    pending_supervisors = SchoolSupervisor.objects.filter(
        is_approved=False
    )

    # RECENT ACTIVITIES
    activities = []
    recent_profiles = UserProfile.objects.select_related('user').order_by('-user__date_joined')[:6]
    for profile in recent_profiles:
        activities.append({
            'time': profile.user.date_joined,
            'message': f"{profile.get_role_display()} account created for {profile.user.username}",
        })

    recent_applications = StudentApplication.objects.order_by('-submitted_at')[:6]
    for application in recent_applications:
        if application.status == 'Pending':
            action = 'submitted an internship application'
        else:
            action = f'{application.status.lower()} an application'

        activities.append({
            'time': application.submitted_at,
            'message': f"{application.full_name} {action}",
        })

    recent_activities = sorted(activities, key=lambda x: x['time'], reverse=True)[:6]

    context = {

        'total_interns': total_interns,

        'total_departments': total_departments,

        'total_comments': total_comments,

        'attendance_data': attendance_data,

        'performance_data': performance_data,

        'intern_names': intern_names,

        'pending_supervisors': pending_supervisors,

        'recent_activities': recent_activities,
    }

    return render(
        request,
        'core/admin_dashboard.html',
        context
    )


@login_required
def pending_school_supervisors(request):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    pending_supervisors = SchoolSupervisor.objects.filter(
        is_approved=False
    )

    return render(
        request,
        'core/pending_school_supervisors.html',
        {
            'pending_supervisors': pending_supervisors,
        }
    )


# =========================================
# POLICE DASHBOARD
# =========================================

@login_required
def police_dashboard(request):

    if request.user.userprofile.role != 'police':
        return redirect('login')

    supervisor = PoliceSupervisor.objects.filter(
        user=request.user
    ).first()

    if not supervisor:
        return HttpResponse("No Police Supervisor profile found.")

    interns = Intern.objects.filter(
        police_supervisor=supervisor
    )

    # Unread messages count for notifications
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
    unread_count = unread_messages.count()
    latest_unread_message = unread_messages.select_related('sender').order_by('-sent_at').first()

    return render(
        request,
        'core/police_dashboard.html',
        {
            'interns': interns,
            'unread_count': unread_count,
            'latest_unread_message': latest_unread_message,
        }
    )


# =========================================
# SCHOOL DASHBOARD
# =========================================

@login_required
def school_dashboard(request):

    if request.user.userprofile.role != 'school':
        return redirect('login')

    supervisor = SchoolSupervisor.objects.filter(
        user=request.user
    ).first()

    if not supervisor:
        return HttpResponse("No School Supervisor profile found.")

    interns = list(Intern.objects.filter(
        school_supervisor=supervisor
    ))

    for intern in interns:
        intern.latest_report = WeeklyReport.objects.filter(
            intern=intern
        ).order_by('-generated_at').first()

    total_interns = len(interns)

    context = {
        'interns': interns,
        'total_interns': total_interns,
    }

    # Unread messages count
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
    context['unread_count'] = unread_messages.count()
    context['latest_unread_message'] = unread_messages.select_related('sender').order_by('-sent_at').first()

    return render(
        request,
        'core/school_dashboard.html',
        context
    )

# =========================================
# REGISTER INTERN
# =========================================

@login_required
def register_intern(request):

    if request.method == 'POST':

        form = InternForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')

    else:
        form = InternForm()

    return render(
        request,
        'core/register_intern.html',
        {'form': form}
    )


# =========================================
# INTERN LIST
# =========================================

@login_required
def intern_list(request):

    profile = request.user.userprofile

    # ADMIN
    if profile.role == 'admin':

        interns = Intern.objects.all()

    # POLICE SUPERVISOR
    elif profile.role == 'police':

        supervisor = PoliceSupervisor.objects.filter(
            user=request.user
        ).first()

        if supervisor:
            interns = Intern.objects.filter(
                police_supervisor=supervisor
            )
        else:
            interns = Intern.objects.none()

    # SCHOOL SUPERVISOR
    elif profile.role == 'school':

        supervisor = SchoolSupervisor.objects.filter(
            user=request.user
        ).first()

        if supervisor:
            interns = Intern.objects.filter(
                school_supervisor=supervisor
            )
        else:
            interns = Intern.objects.none()

    else:

        interns = []

    return render(
        request,
        'core/intern_list.html',
        {
            'interns': interns,
            'user_role': profile.role,
            'is_ict_admin': is_ict_admin(request.user) if profile.role == 'admin' else False
        }
    )


# =========================================
# INTERN DETAILS
# =========================================

@login_required
def intern_detail(request, intern_id):
    intern = get_object_or_404(Intern, id=intern_id)

    # Only allow supervisors/admins or the intern themself to view details
    role = request.user.userprofile.role
    if role == 'intern' and intern.user_id != request.user.id:
        return redirect('login')

    if role == 'police' and (not intern.police_supervisor or intern.police_supervisor.user_id != request.user.id):
        return redirect('login')

    if role == 'school' and (not intern.school_supervisor or intern.school_supervisor.user_id != request.user.id):
        return redirect('login')

    comments = Comment.objects.filter(intern=intern)
    latest_report = WeeklyReport.objects.filter(intern=intern).order_by('-generated_at').first()

    return render(
        request,
        'core/intern_detail.html',
        {
            'intern': intern,
            'comments': comments,
            'latest_report': latest_report,
            'user_role': role,
        }
    )


# =========================================
# ADD COMMENT
# =========================================

@login_required
def add_comment(request, intern_id):

    intern = Intern.objects.get(id=intern_id)

    profile = UserProfile.objects.get(
        user=request.user
    )

    if profile.role == 'admin':
        return HttpResponse(
            "Admins are not allowed to add comments."
        )

    if request.user.userprofile.role not in [
        'police',
        'school'
    ]:
        return redirect('login')

    if request.method == 'POST':

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.intern = intern
            comment.author = request.user

            if profile.role == 'police':
                comment.comment_type = 'Police'

            elif profile.role == 'school':
                comment.comment_type = 'School'

            comment.save()

            return redirect(
                'intern_detail',
                intern_id=intern.id
            )

    else:
        form = CommentForm()

    return render(
        request,
        'core/add_comment.html',
        {'form': form}
    )


# =========================================
# EDIT INTERN
# =========================================

@login_required
def edit_intern(request, intern_id):

    if not is_ict_admin(request.user):
        return redirect('intern_list')

    intern = get_object_or_404(
        Intern,
        id=intern_id
    )

    if request.method == 'POST':

        form = InternForm(
            request.POST,
            instance=intern
        )

        if form.is_valid():
            form.save()

            return redirect(
                'intern_detail',
                intern_id=intern.id
            )

    else:
        form = InternForm(instance=intern)

    return render(
        request,
        'core/edit_intern.html',
        {'form': form}
    )


# =========================================
# DELETE INTERN
# =========================================

@login_required
def delete_intern(request, intern_id):

    if not is_ict_admin(request.user):
        return redirect('intern_list')

    intern = get_object_or_404(
        Intern,
        id=intern_id
    )

    if request.method == 'POST':
        intern.delete()
        return redirect('intern_list')

    return render(
        request,
        'core/delete_intern.html',
        {'intern': intern}
    )

# =========================================
# STUDENT APPLICATION
# =========================================

@login_required
def student_application(request):

    if request.method == 'POST':

        form = StudentApplicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            application = form.save(commit=False)

            # If the submitter is an intern, attach the application to their Intern row
            try:
                if request.user.userprofile.role == 'intern':
                    intern = Intern.objects.filter(user=request.user).first()
                    if intern:
                        application.intern = intern
                        # ensure email matches intern record
                        application.email = intern.email
            except Exception:
                pass

            application.save()

            messages.success(
                request,
                "Application submitted successfully."
            )

            return redirect('application_success')

    else:

        form = StudentApplicationForm()

    return render(
        request,
        'core/student_application.html',
        {
            'form': form
        }
    )

# =========================================
# VIEW APPLICATIONS
# =========================================

@login_required
def application_list(request):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    applications = StudentApplication.objects.all()

    return render(
        request,
        'core/application_list.html',
        {'applications': applications}
    )

# =========================================
# APPROVE APPLICATION
# =========================================

@login_required
def approve_application(request, application_id):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    application = StudentApplication.objects.get(
        id=application_id
    )

    application.status = 'Approved'

    application.save()

    return redirect('application_list')

# =========================================
# REJECT APPLICATION
# =========================================

@login_required
def reject_application(request, application_id):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    application = StudentApplication.objects.get(
        id=application_id
    )

    application.status = 'Rejected'

    application.save()

    return redirect('application_list')

def admin_register(request):
    return render(request, 'core/admin_register.html')


def police_register(request):
    return render(request, 'core/police_register.html')


def school_register(request):
    return render(request, 'core/school_register.html')

@login_required
def application_detail(request, app_id):

    application = StudentApplication.objects.get(id=app_id)

    return render(
        request,
        'core/application_detail.html',
        {
            'application': application
        }
    )

@login_required
def application_list(request):

    applications = StudentApplication.objects.all()

    approved = StudentApplication.objects.filter(
        status='Approved'
    )

    pending = StudentApplication.objects.filter(
        status='Pending'
    )

    context = {

        'applications': applications,
        'approved': approved,
        'pending': pending,

    }

    return render(
        request,
        'core/application_list.html',
        context
    )
    
@login_required
def approve_school(request, id):

    if not is_ict_admin(request.user):
        return redirect('admin_dashboard')

    supervisor = SchoolSupervisor.objects.get(id=id)

    supervisor.is_approved = True

    supervisor.save()

    messages.success(request, 'Supervisor approved successfully.')

    return redirect('admin_dashboard')

@login_required
def manage_users(request):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    admins = UserProfile.objects.filter(role='admin')

    police = PoliceSupervisor.objects.all()

    schools = SchoolSupervisor.objects.all()

    return render(
        request,
        'core/manage_users.html',
        {
            'admins': admins,
            'police': police,
            'schools': schools,
            'is_ict_admin': is_ict_admin(request.user)
        }
    )
    
@login_required
def delete_user(request, user_id):

    if not is_ict_admin(request.user):
        return redirect('manage_users')

    user = User.objects.get(id=user_id)

    user.delete()

    return redirect('manage_users')

@login_required
def activate_intern(request, intern_id):

    if not is_ict_admin(request.user):
        return redirect('intern_list')

    intern = Intern.objects.get(id=intern_id)

    intern.is_active = True

    intern.save()

    return redirect('intern_list')


@login_required
def deactivate_intern(request, intern_id):

    if not is_ict_admin(request.user):
        return redirect('intern_list')

    intern = Intern.objects.get(id=intern_id)

    intern.is_active = False

    intern.save()

    return redirect('intern_list')

@login_required
def supervisor_details(request, supervisor_id):

    supervisor = SchoolSupervisor.objects.get(
        id=supervisor_id
    )

    return render(
        request,
        'core/supervisor_details.html',
        {
            'supervisor': supervisor
        }
    )
    
@login_required
def registered_interns(request):

    registered_interns = UserProfile.objects.filter(
        role='intern'
    )

    context = {
        'registered_interns': registered_interns
    }

    return render(
        request,
        'core/registered_interns.html',
        context
    )


@login_required
def delete_registered_intern(request, user_id):

    if not is_ict_admin(request.user):
        return redirect('registered_interns')

    try:
        user = User.objects.get(id=user_id)
        user.delete()
    except User.DoesNotExist:
        pass

    return redirect('registered_interns')
    
@login_required
def applied_interns(request):

    applications = StudentApplication.objects.all()

    context = {
        'applications': applications
    }

    return render(
        request,
        'core/applied_interns.html',
        context
    )
    
@login_required
def intern_dashboard(request):

    try:

        if request.user.userprofile.role != 'intern':
            return redirect('login')

        # Fetch the logged-in intern's own database row so supervisor updates
        # appear here immediately after form.save() commits them.
        intern = Intern.objects.select_related(
            'police_supervisor__user',
            'school_supervisor__user'
        ).get(user=request.user)

    except (UserProfile.DoesNotExist, Intern.DoesNotExist):

        return redirect('login')

    # COUNTS
    total_interns = Intern.objects.count()

    total_schools = SchoolSupervisor.objects.count()

    # APPLICATION STATUS - always use linked application if present
    application = intern.applications.order_by('-submitted_at').first()

    assigned_supervisor_contacts = []
    if intern.police_supervisor and intern.police_supervisor.user_id:
        assigned_supervisor_contacts.append({
            'role': 'Police Supervisor',
            'name': intern.police_supervisor.full_name,
            'email': intern.police_supervisor.email,
            'user': intern.police_supervisor.user,
            'accent': '#0f4c81',
            'icon': 'bi-shield-check',
        })
    if intern.school_supervisor and intern.school_supervisor.user_id:
        assigned_supervisor_contacts.append({
            'role': 'School Supervisor',
            'name': intern.school_supervisor.full_name,
            'email': intern.school_supervisor.user.email,
            'user': intern.school_supervisor.user,
            'accent': '#10b981',
            'icon': 'bi-mortarboard',
        })

    context = {

        'intern': intern,
        # These aliases keep the template explicit while still reading from
        # the same Intern object that powers reports and supervisor views.
        'attendance_percentage': intern.attendance_percentage,
        'performance_score': intern.performance_score,
        'absent_days': intern.absent_days,
        'late_days': intern.late_days,
        'total_hours': intern.total_hours,
        'weekly_activities': intern.activities_done,
        'last_updated': intern.last_updated,
        'total_interns': total_interns,
        'total_schools': total_schools,
        'application': application,
        'assigned_supervisor_contacts': assigned_supervisor_contacts,
        'can_view_messages': intern.can_view_messages,
        'can_view_performance_tracking': intern.can_view_performance,
        'show_assigned_supervisors': intern.has_assigned_supervisors and intern.can_view_messages,
        'has_submitted_application': intern.has_application,
        'application_notification': intern.application_notification,
        'application_status': intern.application_status,
        'has_assigned_supervisors': intern.has_assigned_supervisors,

    }

    # Unread messages count
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False)
    context['unread_count'] = unread_count = unread_messages.count()
    context['latest_unread_message'] = unread_messages.select_related('sender').order_by('-sent_at').first()

    return render(
        request,
        'core/intern_dashboard.html',
        context
    )


# =========================
# MESSAGING VIEWS
# =========================


def get_allowed_message_users(user):
    """
    Returns the set of User accounts this actor is allowed to message/communicate with.

    This implementation is designed to support:
      - Intern <-> Police Supervisor
      - Intern <-> School Supervisor
    """
    try:
        role = user.userprofile.role
    except UserProfile.DoesNotExist:
        return User.objects.none()

    recipient_ids = set()

    if role == 'intern':
        intern = Intern.objects.filter(user=user).select_related(
            'police_supervisor__user',
            'school_supervisor__user',
        ).first()

        if intern and intern.police_supervisor and intern.police_supervisor.user_id:
            recipient_ids.add(intern.police_supervisor.user_id)
        if intern and intern.school_supervisor and intern.school_supervisor.user_id:
            recipient_ids.add(intern.school_supervisor.user_id)

    elif role == 'police':
        supervisor = PoliceSupervisor.objects.filter(user=user).first()
        if supervisor:
            # Police supervisor -> its assigned interns (intern.user)
            interns = Intern.objects.filter(police_supervisor=supervisor).select_related(
                'user',
                'school_supervisor__user',
            )

            for intern in interns:
                # Key fix: always allow messaging the intern.user for supervisor<->intern
                if intern.user_id:
                    recipient_ids.add(intern.user_id)

                # Keep original capability: police supervisor <-> school supervisor (via intern links)
                if intern.school_supervisor and intern.school_supervisor.user_id:
                    recipient_ids.add(intern.school_supervisor.user_id)

    elif role == 'school':
        supervisor = SchoolSupervisor.objects.filter(user=user).first()
        if supervisor:
            # School supervisor -> its assigned interns (intern.user)
            interns = Intern.objects.filter(school_supervisor=supervisor).select_related(
                'user',
                'police_supervisor__user',
            )

            for intern in interns:
                # Key fix: always allow messaging the intern.user for supervisor<->intern
                if intern.user_id:
                    recipient_ids.add(intern.user_id)

                # Keep original capability: school supervisor <-> police supervisor (via intern links)
                if intern.police_supervisor and intern.police_supervisor.user_id:
                    recipient_ids.add(intern.police_supervisor.user_id)

    recipient_ids.discard(user.id)
    return User.objects.filter(id__in=recipient_ids).order_by('username')


def get_message_contact_label(user):
    """Return a role-aware name for message contacts shown in templates."""
    return MessageForm.recipient_label(user)


def get_message_contacts(user):
    """Build separate contact cards for every account the user can message."""
    contacts = []

    for contact_user in get_allowed_message_users(user):
        contacts.append({
            'user': contact_user,
            'label': get_message_contact_label(contact_user),
        })

    return contacts


def get_message_context(request):
    inbox_messages = Message.objects.filter(receiver=request.user).select_related('sender')
    sent_items = Message.objects.filter(sender=request.user).select_related('receiver')
    unread_count = inbox_messages.filter(is_read=False).count()
    latest_unread_message = inbox_messages.filter(is_read=False).order_by('-sent_at').first()

    conversation_users = {}
    for message in list(inbox_messages[:50]) + list(sent_items[:50]):
        other = message.sender if message.sender_id != request.user.id else message.receiver
        current = conversation_users.get(other.id)
        if current is None or message.sent_at > current['last_message'].sent_at:
            conversation_users[other.id] = {
                'user': other,
                'last_message': message,
                'unread_count': Message.objects.filter(
                    sender=other,
                    receiver=request.user,
                    is_read=False
                ).count()
            }

    conversations = sorted(
        conversation_users.values(),
        key=lambda item: item['last_message'].sent_at,
        reverse=True
    )

    return {
        'inbox_messages': inbox_messages,
        'sent_messages': sent_items,
        'conversations': conversations,
        'message_contacts': get_message_contacts(request.user),
        'unread_count': unread_count,
        'latest_unread_message': latest_unread_message,
    }


@login_required
def messages_dashboard(request):
    if request.user.userprofile.role == 'intern' and not intern_user_is_approved(request.user):
        return redirect('intern_dashboard')

    context = get_message_context(request)
    return render(request, 'core/messages/dashboard.html', context)


@login_required
def inbox(request):
    if request.user.userprofile.role == 'intern' and not intern_user_is_approved(request.user):
        return redirect('intern_dashboard')

    context = get_message_context(request)
    return render(request, 'core/messages/inbox.html', context)


@login_required
def sent_messages(request):
    if request.user.userprofile.role == 'intern' and not intern_user_is_approved(request.user):
        return redirect('intern_dashboard')

    context = get_message_context(request)
    return render(request, 'core/messages/sent.html', context)


@login_required
def compose_message(request):
    if request.user.userprofile.role == 'intern' and not intern_user_is_approved(request.user):
        return redirect('intern_dashboard')

    allowed_receivers = get_allowed_message_users(request.user)
    requested_receiver_id = request.GET.get('receiver')
    initial_receiver = None

    if requested_receiver_id:
        initial_receiver = allowed_receivers.filter(id=requested_receiver_id).first()

    if request.method == 'POST':
        form = MessageForm(
            request.POST,
            request.FILES,
            allowed_receivers=allowed_receivers
        )
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.status = 'delivered'
            msg.is_read = False
            msg.save()
            messages.success(request, 'Message sent successfully.')
            return redirect('sent_messages')
    else:
        form = MessageForm(
            allowed_receivers=allowed_receivers,
            initial_receiver=initial_receiver
        )

    context = get_message_context(request)
    context.update({
        'form': form,
        'allowed_receivers_count': allowed_receivers.count(),
    })
    return render(request, 'core/messages/compose.html', context)


@login_required
def conversation_view(request, user_id):
    if request.user.userprofile.role == 'intern' and not intern_user_is_approved(request.user):
        return redirect('intern_dashboard')

    other = get_object_or_404(User, id=user_id)

    participant_messages = Message.objects.filter(
        Q(sender=request.user, receiver=other) |
        Q(sender=other, receiver=request.user)
    )
    is_allowed_recipient = get_allowed_message_users(request.user).filter(id=other.id).exists()

    if other == request.user or not is_allowed_recipient:
        return redirect('login')

    conv_messages = participant_messages.select_related('sender', 'receiver').order_by('sent_at')

    # Mark messages received by current user as read
    Message.objects.filter(sender=other, receiver=request.user, is_read=False).update(is_read=True, status='read')

    if request.method == 'POST':
        body = request.POST.get('message_body', '').strip()
        subject = request.POST.get('subject', '') or f"Re: Conversation with {other.username}"
        if body:
            msg = Message.objects.create(
                sender=request.user,
                receiver=other,
                subject=subject,
                message_body=body,
                status='delivered'
            )
            messages.success(request, 'You have sent a reply.')
            return redirect('conversation_view', user_id=other.id)

    context = get_message_context(request)
    context.update({
        'other': other,
        'conversation_messages': conv_messages,
    })
    return render(request, 'core/messages/conversation.html', context)
    
def account_created(request):

    return render(
        request,
        'core/account_created.html'
    )
    
def intern_register(request):

    if request.method == 'POST':

        full_name = request.POST['full_name']
        institution = request.POST['institution']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        profile = user.userprofile
        profile.role = 'intern'
        profile.save()

        # Create intern
        Intern.objects.create(
            user=user,
            full_name=full_name,
            institution=institution,
            email=email
        )

        # SUCCESS MESSAGE
        messages.success(
            request,
            "Thank you for creating your account successfully. "
            "Please go back to the Login page to access your Intern Dashboard for more updates."
        )

        return redirect('account_created')

    return render(request, 'core/intern_register.html')
    
def create_account(request):

    return render(
        request,
        'core/create_account.html'
    )
    
def discover(request):

    return render(
        request,
        'core/discover.html'
    )
    
def account_pending(request):

    return render(
        request,
        'core/account_pending.html'
    )
    
@login_required
def application_success(request):

    return render(
        request,
        'core/application_success.html'
    )
    
@login_required
def intern_progress(request):

    if request.user.userprofile.role != 'intern':
        return redirect('login')

    intern = Intern.objects.get(user=request.user)

    if not intern_user_is_approved(request.user):
        messages.warning(
            request,
            'Performance tracking is available after your internship application has been approved.'
        )
        return redirect('intern_dashboard')

    comments = Comment.objects.filter(
        intern=intern,
        comment_type='School'
    )

    latest_report = WeeklyReport.objects.filter(intern=intern).order_by('-generated_at').first()

    context = {

        'intern': intern,
        'comments': comments,
        'latest_report': latest_report,

    }

    return render(
        request,
        'core/intern_progress.html',
        context
    )


def intern_user_is_approved(user):
    try:
        if user.userprofile.role != 'intern':
            return True
    except UserProfile.DoesNotExist:
        return False

    intern = Intern.objects.filter(user=user).first()
    return bool(intern and intern.is_dashboard_approved)
    
@login_required
def update_intern(request, intern_id):

    if request.user.userprofile.role != 'police':
        return redirect('login')

    intern = get_object_or_404(
        Intern,
        id=intern_id
    )

    if request.method == 'POST':

        form = InternUpdateForm(
            request.POST,
            instance=intern
        )

        if form.is_valid():

            # Save the Intern model row directly; the intern dashboard and PDF
            # report read these same fields, so no manual synchronization is needed.
            form.save()

            messages.success(
                request,
                'Intern updated successfully.'
            )

            return redirect('update_success')

    else:

        form = InternUpdateForm(
            instance=intern
        )

    return render(
        request,
        'core/update_intern.html',
        {
            'form': form,
            'intern': intern
        }
    )


@login_required
def update_success(request):

    if request.user.userprofile.role != 'police':
        return redirect('login')

    return render(
        request,
        'core/update_success.html'
    )
    
@login_required
def add_police_supervisor(request):

    if not is_ict_admin(request.user):
        return redirect('manage_users')

    if request.method == 'POST':

        form = PoliceSupervisorForm(request.POST)

        if form.is_valid():

            user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email']
            )
            user.set_password(form.cleaned_data['password'])
            user.save()

            UserProfile.objects.create(
                user=user,
                role='police'
            )

            supervisor = form.save(commit=False)
            supervisor.user = user
            supervisor.save()

            messages.success(
                request,
                'Police Supervisor account created successfully.'
            )

            return redirect('admin_dashboard')

        messages.error(request, 'Please correct the errors below and try again.')

    else:

        form = PoliceSupervisorForm()

    return render(
        request,
        'core/add_police_supervisor.html',
        {'form': form}
    )

@login_required
def generate_weekly_report(request, intern_id):

    intern = get_object_or_404(Intern, id=intern_id)

    # Access control: interns may only generate/view their own report.
    role = request.user.userprofile.role
    if role == 'intern' and intern.user_id != request.user.id:
        messages.warning(request, 'You are not allowed to access that report.')
        return redirect('intern_dashboard')

    # =========================
    # CREATE REPORT FOLDER
    # =========================
    reports_folder = os.path.join(
        settings.MEDIA_ROOT,
        'weekly_reports'
    )

    os.makedirs(
        reports_folder,
        exist_ok=True
    )

    # =========================
    # FILE NAME
    # =========================
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"report_{intern.id}_{timestamp}.pdf"

    filepath = os.path.join(
        reports_folder,
        filename
    )

    # =========================
    # GENERATE CHART (optional)
    # If matplotlib is not installed we'll skip chart generation
    # =========================
    chart_path = os.path.join(
        settings.MEDIA_ROOT,
        f'chart_{intern.id}_{timestamp}.jpg'
    )

    has_matplotlib = False
    try:
        import matplotlib.pyplot as plt
        has_matplotlib = True
    except Exception:
        has_matplotlib = False

    if has_matplotlib:
        try:
            plt.figure(figsize=(4, 3))

            metrics = ['Attendance', 'Performance']

            values = [intern.attendance_percentage, intern.performance_score]

            plt.bar(metrics, values)
            plt.title('Intern Performance Summary')
            plt.ylim(0, 100)
            plt.savefig(chart_path)
            plt.close()
        except Exception:
            # If anything fails during plotting, ensure chart_path is not used
            chart_path = None
    else:
        chart_path = None
    
    qr_data = f"""
    Intern: {intern.full_name}
    Performance: {intern.performance_score}%
    Attendance: {intern.attendance_percentage}%
    """

    # Generate QR code if qrcode library is available
    qr_path = None
    try:
        import qrcode
        qr = qrcode.make(qr_data)
        qr_path = os.path.join(settings.MEDIA_ROOT, f'qr_{intern.id}_{timestamp}.png')
        qr.save(qr_path)
    except Exception:
        qr_path = None

    # =========================
    # CREATE PDF
    # =========================
    page_width, page_height = letter
    p = canvas.Canvas(filepath, pagesize=letter)

    margin = 50
    content_width = page_width - (margin * 2)

    # =========================
    # PAGE BORDER
    # =========================
    p.setLineWidth(3)
    p.rect(
        margin / 2,
        margin / 2,
        page_width - margin,
        page_height - margin,
        stroke=1,
        fill=0
    )

    # =========================
    # PAGE BACKGROUND LOGO
    # =========================
    logo_path = os.path.join(
        settings.MEDIA_ROOT,
        'images',
        'police_logo.jpg'
    )

    logo_size = 0
    if os.path.exists(logo_path):
        p.saveState()
        try:
            p.setFillAlpha(0.08)
        except Exception:
            pass
        p.drawImage(
            logo_path,
            margin,
            margin,
            width=content_width,
            height=page_height - (margin * 2),
            preserveAspectRatio=True,
            mask='auto'
        )
        p.restoreState()

        # =========================
        # TITLE + SINGLE LOGO
        # =========================
        logo_size = 85

    if os.path.exists(logo_path):
        p.drawImage(
            logo_path,
            margin,
            page_height - margin - logo_size,
            width=logo_size,
            height=logo_size,
            mask='auto'
        )

    p.setFont("Helvetica-Bold", 22)

    # =========================
    # TITLE
    # =========================
    title_x = margin + logo_size + 20

    p.setFont("Helvetica-Bold", 22)
    p.drawString(
        title_x,
        page_height - margin - 30,
        "WEEKLY INTERN REPORT"
    )

    # HEADQUARTERS NAME
    p.setFont("Helvetica-Bold", 11)
    p.drawString(
        title_x,
        page_height - margin - 52,
        "Malawi Police Headquarters, Area 30"
    )

    # GENERATED DATE
    p.setFont("Helvetica", 10)
    p.drawString(
        title_x,
        page_height - margin - 72,
        f"Generated: {date.today().strftime('%B %d, %Y')}"
    )

    # =========================
    # INTERN DETAILS
    # =========================
    p.setFont("Helvetica-Bold", 11)
    details_x = margin
    details_y = page_height - margin - logo_size - 30
    details_mid = margin + content_width / 2 + 10

    p.drawString(details_x, details_y, "Intern Name:")
    p.drawString(details_mid, details_y, "Email:")
    p.setFont("Helvetica", 11)
    p.drawString(details_x + 100, details_y, intern.full_name)
    p.drawString(details_mid + 50, details_y, intern.email)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(details_x, details_y - 18, "Institution:")
    p.drawString(details_mid, details_y - 18, "Phone:")
    p.setFont("Helvetica", 11)
    p.drawString(details_x + 100, details_y - 18, intern.institution)
    p.drawString(details_mid + 40, details_y - 18, intern.phone)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(details_x, details_y - 36, "Program:")
    p.setFont("Helvetica", 11)
    p.drawString(details_x + 60, details_y - 36, intern.program)

    # =========================
    # ATTENDANCE DETAILS
    # =========================
    p.setFont("Helvetica-Bold", 12)
    table_x = margin
    table_y = details_y - 80
    row_height = 22
    rows = [
        ("Attendance Percentage", f"{intern.attendance_percentage}%"),
        ("Present Days", f"{intern.present_days}"),
        ("Absent Days", f"{intern.absent_days}"),
        ("Late Days", f"{intern.late_days}"),
        ("Total Hours Worked", f"{intern.total_hours}")
    ]

    table_height = row_height * len(rows)
    p.drawString(table_x, table_y + 4, "Attendance Summary")
    p.setLineWidth(1.5)
    p.rect(
        table_x,
        table_y - table_height,
        content_width,
        table_height,
        stroke=1,
        fill=0
    )
    p.line(
        table_x + 300,
        table_y,
        table_x + 300,
        table_y - table_height
    )

    p.setFont("Helvetica", 10)
    for index, row in enumerate(rows):
        y = table_y - (index * row_height) - 16
        p.drawString(table_x + 8, y, row[0])
        p.drawString(table_x + 310, y, row[1])

    # =========================
    # CHART BELOW ATTENDANCE
    # =========================
    chart_width = 260
    chart_height = 140
    chart_x = margin
    chart_y = table_y - table_height - chart_height - 20
    
    # =========================
    # PERFORMANCE SCORE ABOVE CHART
    # =========================
    p.setFont("Helvetica-Bold", 12)

    p.drawString(
        chart_x,
        chart_y - 20,
        f"Performance Score: {intern.performance_score}%"
    )

    if chart_path and os.path.exists(chart_path):
        p.drawImage(
            chart_path,
            chart_x,
            chart_y,
            width=chart_width,
            height=chart_height,
            mask='auto'
        )

    # =========================
    # ACTIVITIES DONE
    # =========================
    activities = str(intern.activities_done or "No activities recorded")

    def wrap_text(text, max_chars=40):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= max_chars:
                current = f"{current} {word}".strip()
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    activity_lines = wrap_text(activities, 40)
    activity_box_x = chart_x + chart_width + 30
    activity_box_y = chart_y + chart_height - 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(activity_box_x, activity_box_y, "Activities Done:")
    p.setFont("Helvetica", 10)
    current_y = activity_box_y - 16
    for line in activity_lines[:8]:
        p.drawString(activity_box_x + 8, current_y, line)
        current_y -= 14
    if len(activity_lines) > 8:
        p.drawString(activity_box_x + 8, current_y, "...")

    # Keep y for the next section below the chart
    y = chart_y - 40

        # =========================
    # START LOWER CONTENT AREA
    # =========================
    section_y = chart_y - 40

    # =========================
    # WARNING MESSAGE
    # =========================
    p.setFont("Helvetica-Bold", 12)

    p.drawString(
        50,
        section_y,
        "Warning Message:"
    )

    p.setFont("Helvetica", 11)

    warning_text = str(
        intern.warning_message or "None"
    )

    p.drawString(
        70,
        section_y - 20,
        warning_text
    )

    # =========================
    # APPRECIATION MESSAGE
    # =========================
    appreciation_y = section_y - 60

    p.setFont("Helvetica-Bold", 12)

    p.drawString(
        50,
        appreciation_y,
        "Appreciation Message:"
    )

    p.setFont("Helvetica", 11)

    appreciation_text = str(
        intern.appreciation_message or "None"
    )

    p.drawString(
        70,
        appreciation_y - 20,
        appreciation_text
    )

    # =========================
    # OVERALL RATING
    # =========================
    average_score = (
        intern.performance_score +
        intern.attendance_percentage
    ) / 2

    if average_score >= 85:

        rating = "Excellent"

    elif average_score >= 70:

        rating = "Very Good"

    elif average_score >= 50:

        rating = "Good"

    elif average_score >= 40:

        rating = "Satisfactory"

    else:

        rating = "Needs Improvement"

    rating_y = appreciation_y - 60

    p.setFont("Helvetica-Bold", 12)

    p.drawString(
        50,
        rating_y,
        f"Overall Weekly Rating: {rating}"
    )

    # =========================
    # QR CODE
    # =========================
    qr_y = margin + 40

    if os.path.exists(qr_path):

        p.drawImage(
            qr_path,
            page_width - margin - 110,
            qr_y,
            width=90,
            height=90,
            mask='auto'
        )

    # =========================
    # SIGNATURE
    # =========================
    signature_y = margin + 55

    p.setFont("Helvetica-Bold", 11)

    p.drawString(
        50,
        signature_y,
        "Police Supervisor Signature:"
    )

    p.line(
        250,
        signature_y,
        450,
        signature_y
    )

    # =========================
    # SAVE PDF
    # =========================
    p.save()

    # =========================
    # SAVE REPORT TO DATABASE
    # =========================
    WeeklyReport.objects.create(

        intern=intern,

        week_start=date.today(),

        week_end=date.today(),

        pdf_file=f'weekly_reports/{filename}',

        overall_rating=rating
    )

    # =========================
    # DOWNLOAD PDF
    # =========================
    return FileResponse(
        open(filepath, 'rb'),
        as_attachment=True,
        filename=filename
    )
    
@login_required
def assign_supervisors(request, application_id):

    if request.user.userprofile.role != 'admin':
        return redirect('login')

    application = get_object_or_404(
        StudentApplication,
        id=application_id
    )

    police_supervisors = PoliceSupervisor.objects.all()

    school_supervisors = SchoolSupervisor.objects.filter(
        is_approved=True
    )

    if request.method == 'POST':

        police_id = request.POST.get(
            'police_supervisor'
        )

        school_id = request.POST.get(
            'school_supervisor'
        )

        police_supervisor = PoliceSupervisor.objects.get(
            id=police_id
        )

        school_supervisor = SchoolSupervisor.objects.get(
            id=school_id
        )

        applicant_user = User.objects.filter(
            email__iexact=application.email,
            userprofile__role='intern'
        ).first()

        # Prefer an Intern row explicitly linked to the application
        intern = None
        if application.intern:
            intern = application.intern

        # Fallback: if the application email matches an existing user
        if intern is None and applicant_user:
            intern = Intern.objects.filter(user=applicant_user).first()

        # Fallback: try to find an unlinked intern record by email
        if intern is None:
            intern = Intern.objects.filter(
                email__iexact=application.email,
                user__isnull=True
            ).order_by('-is_approved', '-id').first()

        if intern is None:
            intern = Intern()

        if applicant_user and intern.user_id is None:
            intern.user = applicant_user

        # Update intern from application and assign supervisors
        intern.full_name = application.full_name
        intern.email = application.email
        intern.institution = application.school_name
        intern.program = application.program
        intern.phone = application.phone_number
        intern.gender = application.gender
        intern.police_supervisor = police_supervisor
        intern.school_supervisor = school_supervisor
        intern.is_approved = True
        application.status = 'Approved'

        if not intern.blood_group:
            intern.blood_group = 'N/A'
        if not intern.marital_status:
            intern.marital_status = 'N/A'
        if not intern.address:
            intern.address = 'N/A'

        intern.save()
        # Link the application to the resolved/created intern and persist status
        application.intern = intern
        application.save(update_fields=['status', 'intern'])

        messages.success(
            request,
            'Supervisors assigned successfully.'
        )

        return redirect('application_list')

    context = {

        'application': application,
        'police_supervisors': police_supervisors,
        'school_supervisors': school_supervisors

    }

    return render(
        request,
        'core/assign_supervisors.html',
        context
    )
    
@login_required
def all_reports(request):

    role = request.user.userprofile.role

    if role in ['admin', 'police']:
        reports = WeeklyReport.objects.select_related('intern').order_by('-id')
    elif role == 'intern':
        reports = WeeklyReport.objects.select_related('intern').filter(intern__user=request.user).order_by('-id')
    else:
        return redirect('login')

    return render(
        request,
        'core/all_reports.html',
        {
            'reports': reports,
            'user_role': role
        }
    )


@login_required
def delete_report(request, report_id):

    if request.user.userprofile.role not in ['admin', 'police']:
        return redirect('login')

    report = get_object_or_404(WeeklyReport, id=report_id)

    if report.pdf_file:
        report.pdf_file.delete(save=False)

    report.delete()
    messages.success(request, 'Report deleted successfully.')

    return redirect('all_reports')


@login_required
def admin_settings(request):
    if request.user.userprofile.role != 'admin':
        return redirect('login')

    # System information (singleton-ish)
    system_info, _ = SystemInformation.objects.get_or_create(
        id=1,
        defaults={
            'system_name': 'Police Intern Tracking System',
            'organization_name': 'Police Headquarters',
            'contact_email': request.user.email or '',
            'contact_phone_number': '',
        },
    )

    # Admin settings profile
    settings_profile, _ = AdminSettingsProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': getattr(request.user, 'username', ''),
            'email': request.user.email or '',
        },
    )

    if request.method == 'POST':
        # Distinguish which card was submitted
        if request.POST.get('action') == 'save_system':
            system_form = SystemInformationForm(
                request.POST,
                request.FILES,
                instance=system_info,
            )
            profile_form = AdminSettingsProfileForm(instance=settings_profile)

            if system_form.is_valid():
                system_form.save()
                messages.success(request, 'System information updated successfully.')
                return redirect('admin_settings')

        elif request.POST.get('action') == 'save_profile':
            profile_form = AdminSettingsProfileForm(
                request.POST,
                request.FILES,
                instance=settings_profile,
            )
            system_form = SystemInformationForm(instance=system_info)

            if profile_form.is_valid():
                profile_form.save()
                # Keep User.email in sync for auth/email usage.
                request.user.email = profile_form.cleaned_data.get('email', request.user.email)
                request.user.save(update_fields=['email'])
                messages.success(request, 'Profile updated successfully.')
                return redirect('admin_settings')

        else:
            system_form = SystemInformationForm(instance=system_info)
            profile_form = AdminSettingsProfileForm(instance=settings_profile)

    else:
        system_form = SystemInformationForm(instance=system_info)
        profile_form = AdminSettingsProfileForm(instance=settings_profile)

    change_password_form = AdminChangePasswordForm(user=request.user)

    context = {
        'system_form': system_form,
        'profile_form': profile_form,
        'change_password_form': change_password_form,
        'system_info': system_info,
        'settings_profile': settings_profile,
    }
    return render(request, 'core/admin_settings.html', context)


@login_required
def change_admin_password(request):
    if request.user.userprofile.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = AdminChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('admin_settings')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = AdminChangePasswordForm(user=request.user)

    # Render the same template; the other forms will still show current data.
    # We reuse admin_settings to keep the UI consistent.
    # Instead of calling admin_settings directly, keep it explicit.
    system_info, _ = SystemInformation.objects.get_or_create(
        id=1,
        defaults={
            'system_name': 'Police Intern Tracking System',
            'organization_name': 'Police Headquarters',
        },
    )

    settings_profile, _ = AdminSettingsProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': getattr(request.user, 'username', ''),
            'email': request.user.email or '',
        },
    )

    context = {
        'system_form': SystemInformationForm(instance=system_info),
        'profile_form': AdminSettingsProfileForm(instance=settings_profile),
        'change_password_form': form,
        'system_info': system_info,
        'settings_profile': settings_profile,
    }
    return render(request, 'core/admin_settings.html', context)

