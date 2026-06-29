from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Landing Page
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('police-dashboard/', views.police_dashboard, name='police_dashboard'),
    path('school-dashboard/', views.school_dashboard, name='school_dashboard'),
    path(
    'intern-dashboard/',
    views.intern_dashboard,
    name='intern_dashboard'
),

    # Intern Management
    path('register-intern/', views.register_intern, name='register_intern'),
    path('interns/', views.intern_list, name='intern_list'),
    path('intern/<int:intern_id>/', views.intern_detail, name='intern_detail'),
    path('add-comment/<int:intern_id>/', views.add_comment, name='add_comment'),
    path('edit-intern/<int:intern_id>/', views.edit_intern, name='edit_intern'),
    path('delete-intern/<int:intern_id>/', views.delete_intern, name='delete_intern'),

    # Forgot Password Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ), name='password_reset_complete'),

    path(
    'applications/',
    views.application_list,
    name='application_list'
),
    
path(
    'register-school/',
    views.register_school,
    name='register_school'
),
    
path(
    'student-application/',
    views.student_application,
    name='student_application'
),

path(
    'approve-application/<int:application_id>/',
    views.approve_application,
    name='approve_application'
),

path(
    'reject-application/<int:application_id>/',
    views.reject_application,
    name='reject_application'
),

path(
    'application/<int:app_id>/',
    views.application_detail,
    name='application_detail'
),

path(
    'add-admin/',
    views.add_admin,
    name='add_admin'
),

path(
    'view-admins/',
    views.view_admins,
    name='view_admins'
),

path(
    'application-success/',
    views.application_success,
    name='application_success'
),

path(
    'intern-progress/',
    views.intern_progress,
    name='intern_progress'
),

path(
    'update-intern/<int:intern_id>/',
    views.update_intern,
    name='update_intern'
),

path(
    'update-success/',
    views.update_success,
    name='update_success'
),

path(
    'generate-report/<int:intern_id>/',
    views.generate_weekly_report,
    name='generate_report'
),

path(
    'add-police-supervisor/',
    views.add_police_supervisor,
    name='add_police_supervisor'
),

path(
    'all-reports/',
    views.all_reports,
    name='all_reports'
),

path(
    'delete-report/<int:report_id>/',
    views.delete_report,
    name='delete_report'
),

path(
    'approve-application/<int:app_id>/',
    views.approve_application,
    name='approve_application'
),

path(
    'reject-application/<int:app_id>/',
    views.reject_application,
    name='reject_application'
),

path(
    'account-pending/',
    views.account_pending,
    name='account_pending'
),

path(
    'registered-interns/',
    views.registered_interns,
    name='registered_interns'
),

path(
    'delete-registered-intern/<int:user_id>/',
    views.delete_registered_intern,
    name='delete_registered_intern'
),

path(
    'approve-school/<int:id>/',
    views.approve_school,
    name='approve_school'
),

path(
    'pending-school-supervisors/',
    views.pending_school_supervisors,
    name='pending_school_supervisors'
),

path(
    'create-account/',
    views.create_account,
    name='create_account'
),

path(
    'manage-users/',
    views.manage_users,
    name='manage_users'
),

path(
    'delete-user/<int:user_id>/',
    views.delete_user,
    name='delete_user'
),

path(
    'activate-intern/<int:intern_id>/',
    views.activate_intern,
    name='activate_intern'
),

path(
    'deactivate-intern/<int:intern_id>/',
    views.deactivate_intern,
    name='deactivate_intern'
),

path(
    'delete-intern/<int:intern_id>/',
    views.delete_intern,
    name='delete_intern'
),

path(
    'supervisor-details/<int:supervisor_id>/',
    views.supervisor_details,
    name='supervisor_details'
),

path(
    'account-created/',
    views.account_created,
    name='account_created'
),

path(
    'discover/',
    views.discover,
    name='discover'
),

path(
    'assign-supervisors/<int:application_id>/',
    views.assign_supervisors,
    name='assign_supervisors'
), 

path(
    'intern-register/',
    views.intern_register,
    name='intern_register'
),

path(
    'messages/',
    views.messages_dashboard,
    name='messages_dashboard'
),

path(
    'messages/inbox/',
    views.inbox,
    name='inbox'
),

path(
    'messages/sent/',
    views.sent_messages,
    name='sent_messages'
),

path(
    'messages/compose/',
    views.compose_message,
    name='compose_message'
),

path(
    'messages/conversation/<int:user_id>/',
    views.conversation_view,
    name='conversation_view'
),

    # Settings
    path(
        'settings/',
        views.admin_settings,
        name='admin_settings'
    ),
    path(
        'settings/change-password/',
        views.change_admin_password,
        name='change_admin_password'
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
