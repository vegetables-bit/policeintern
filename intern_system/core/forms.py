from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import (
    AdminProfile,
    AdminSettingsProfile,
    Comment,
    Intern,
    PoliceSupervisor,
    SchoolSupervisor,
    StudentApplication,
    SystemInformation,
    Message,
)


class AdminRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already in use.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data

    class Meta:
        model = AdminProfile
        fields = ['full_name', 'position', 'department']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PoliceSupervisorForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already in use.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    class Meta:
        model = PoliceSupervisor
        fields = [
            'full_name',
            'police_id',
            'rank',
            'department',
            'station',
            'phone',
            'email',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'police_id': forms.TextInput(attrs={'class': 'form-control'}),
            'rank': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'station': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class SchoolSupervisorForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already in use.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    class Meta:
        model = SchoolSupervisor
        fields = [
            'full_name',
            'institution',
            'institution_name',
            'employee_id',
            'department',
            'position',
            'phone',
            'email',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'institution_name': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class InternForm(forms.ModelForm):
    class Meta:
        model = Intern
        fields = [
            'full_name',
            'gender',
            'age',
            'blood_group',
            'marital_status',
            'phone',
            'email',
            'address',
            'institution',
            'program',
            'start_date',
            'end_date',
            'school_supervisor',
            'police_supervisor',
            'is_active',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'marital_status': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'program': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'school_supervisor': forms.Select(attrs={'class': 'form-control'}),
            'police_supervisor': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InternUpdateForm(forms.ModelForm):
    class Meta:
        model = Intern
        # Police supervisors update these model fields directly; form.save()
        # persists the same values later shown on dashboards and reports.
        fields = [
            'full_name',                # Intern Name
            'email',
            'institution',
            'phone',
            'program',
            'attendance_percentage',
            'present_days',
            'absent_days',
            'late_days',
            'total_hours',
            'performance_score',
            'activities_done',
        ]

        labels = {
            'attendance_percentage': 'Attendance Percentage',
            'present_days': 'Present Days',
            'absent_days': 'Absent Days',
            'late_days': 'Late Days',
            'total_hours': 'Total Hours Worked',
            'performance_score': 'Performance Score',
            'activities_done': 'Weekly Activities',
        }

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'program': forms.TextInput(attrs={'class': 'form-control'}),

            'attendance_percentage': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'max': '100'}
            ),

            'present_days': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),

            'absent_days': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),

            'late_days': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),

            'total_hours': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0'}
            ),

            'performance_score': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'max': '100'}
            ),

            'activities_done': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your comment here...'
            }),
        }


class StudentApplicationForm(forms.ModelForm):
    class Meta:
        model = StudentApplication
        fields = [
            'full_name',
            'gender',
            'date_of_birth',
            'reg_number',
            'school_name',
            'program',
            'semester',
            'year',
            'department',
            'email',
            'phone_number',
            'school_id',
            'national_id',
            'recommendation_letter',
            'transcript',
            'application_letter',
            'photo',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reg_number': forms.TextInput(attrs={'class': 'form-control'}),
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'program': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'school_id': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png,.jpeg'}),
            'national_id': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png,.jpeg'}),
            'recommendation_letter': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'transcript': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.png,.jpeg'}),
            'application_letter': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.png,.jpeg'}),
        }


class SystemInformationForm(ModelForm):
    class Meta:
        model = SystemInformation
        fields = [
            'system_name',
            'organization_name',
            'contact_email',
            'contact_phone_number',
            'system_logo',
        ]
        widgets = {
            'system_name': forms.TextInput(attrs={'class': 'form-control'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'system_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.png,.jpeg,.gif'}),
        }


class AdminSettingsProfileForm(ModelForm):
    class Meta:
        model = AdminSettingsProfile
        fields = [
            'full_name',
            'email',
            'phone_number',
            'profile_picture',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.png,.jpeg,.gif'}),
        }


class AdminChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Current Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm New Password'
    )


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        allowed_receivers = kwargs.pop('allowed_receivers', None)
        initial_receiver = kwargs.pop('initial_receiver', None)
        super().__init__(*args, **kwargs)
        if allowed_receivers is not None:
            self.fields['receiver'].queryset = allowed_receivers
            grouped_choices = []
            groups = {
                'Police Supervisors': [],
                'School Supervisors': [],
                'Interns': [],
            }
            for user in allowed_receivers:
                label = self.recipient_label(user)
                if label.startswith('Police Supervisor'):
                    groups['Police Supervisors'].append((user.pk, label))
                elif label.startswith('School Supervisor'):
                    groups['School Supervisors'].append((user.pk, label))
                elif label.startswith('Intern'):
                    groups['Interns'].append((user.pk, label))
                else:
                    groups.setdefault('Other', []).append((user.pk, label))

            for title, choices in groups.items():
                if choices:
                    grouped_choices.append((title, sorted(choices, key=lambda item: item[1].lower())))
            self.fields['receiver'].choices = grouped_choices
        if initial_receiver is not None:
            self.fields['receiver'].initial = initial_receiver
        self.fields['receiver'].empty_label = 'Select recipient'
        self.fields['receiver'].widget.attrs.setdefault('class', 'form-control')

    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'message_body', 'attachment']
        widgets = {
            'receiver': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

    @staticmethod
    def recipient_label(user):
        display_name = user.get_full_name() or user.username

        try:
            role = user.userprofile.role
        except Exception:
            return display_name

        if role == 'police':
            supervisor = PoliceSupervisor.objects.filter(user=user).first()
            name = supervisor.full_name if supervisor else display_name
            return f'Police Supervisor - {name}'

        if role == 'school':
            supervisor = SchoolSupervisor.objects.filter(user=user).first()
            name = supervisor.full_name if supervisor else display_name
            return f'School Supervisor - {name}'

        if role == 'intern':
            intern = Intern.objects.filter(user=user).first()
            name = intern.full_name if intern else display_name
            return f'Intern - {name}'

        return display_name
