from django import forms
from django.contrib.auth.models import User

from .models import Complaint, Comment, Profile


# =========================================================
# COMPLAINT FORM
# =========================================================

class ComplaintForm(forms.ModelForm):
    """
    Student submits a complaint.

    Category and priority are NOT entered manually.
    They are automatically detected by the classifier.
    """

    class Meta:
        model = Complaint
        fields = ["title", "description", "location", "image"]

        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Describe the issue in your own words...",
            }),
        }


# =========================================================
# ASSIGNMENT FORM
# =========================================================

class AssignmentForm(forms.ModelForm):
    """
    Admin uses this form to assign a complaint
    to a verified service staff member.
    """

    class Meta:
        model = Complaint
        fields = ["assigned_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # IMPORTANT:
        # Only staff members who are verified by admin
        # can be assigned to complaints.

        self.fields["assigned_to"].queryset = User.objects.filter(
            profile__role="staff",
            profile__is_verified=True
        )

        self.fields["assigned_to"].label = "Assign to Staff"


# =========================================================
# RESOLUTION FORM
# =========================================================

class ResolutionForm(forms.ModelForm):
    """
    Staff enters remarks when resolving a complaint.
    """

    class Meta:
        model = Complaint
        fields = []

    remarks = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "rows": 4,
            "placeholder": "Describe the work completed and resolution..."
        })
    )


# =========================================================
# COMMENT FORM
# =========================================================

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["text"]

        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Type your message here...",
                "style": (
                    "width: 100%; "
                    "padding: 10px; "
                    "border-radius: 8px; "
                    "border: 1px solid #d1d5db; "
                    "resize: none;"
                )
            }),
        }

        labels = {
            "text": ""
        }


# =========================================================
# ADMIN — CREATE USER
# =========================================================

class UserCreateForm(forms.ModelForm):
    """
    Admin uses this form to create a new user.

    The admin can select:
    Student
    Staff
    Admin
    """

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter password"
            }
        ),
        required=True
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm password"
            }
        ),
        required=True
    )

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        required=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "role",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "placeholder": "Username"
            }),

            "first_name": forms.TextInput(attrs={
                "placeholder": "First name"
            }),

            "last_name": forms.TextInput(attrs={
                "placeholder": "Last name"
            }),

            "email": forms.EmailInput(attrs={
                "placeholder": "Email address"
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:

            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


# =========================================================
# ADMIN — EDIT USER
# =========================================================

class UserEditForm(forms.ModelForm):
    """
    Admin uses this form to edit an existing user's
    basic information and role.
    """

    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        required=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
        ]

        widgets = {
            "username": forms.TextInput(),

            "first_name": forms.TextInput(),

            "last_name": forms.TextInput(),

            "email": forms.EmailInput(),
        }


# =========================================================
# ADMIN — STAFF INFORMATION
# =========================================================

# =========================================================
# ADMIN — CREATE STAFF
# =========================================================

class StaffCreateForm(forms.ModelForm):
    """
    Admin uses this form to create a new staff member.

    This form includes login credentials because a new
    staff member needs a username and password.
    """

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Username"
        })
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "First name"
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Last name"
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "Email address"
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter password"
        })
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm password"
        })
    )

    class Meta:
        model = Profile

        fields = [
            "employee_id",
            "department",
            "phone_number",
            "is_verified",
        ]

        widgets = {
            "employee_id": forms.TextInput(attrs={
                "placeholder": "Example: STF001"
            }),

            "department": forms.TextInput(attrs={
                "placeholder": "Example: Electrical Maintenance"
            }),

            "phone_number": forms.TextInput(attrs={
                "placeholder": "Example: 9876543210"
            }),
        }

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:

            if password != confirm_password:

                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


# =========================================================
# ADMIN — EDIT STAFF
# =========================================================
class StaffEditForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "readonly": "readonly"
        })
    )

    first_name = forms.CharField(
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        max_length=150,
        required=False
    )

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = Profile

        fields = [
            "employee_id",
            "department",
            "phone_number",
            "is_verified",
        ]

        widgets = {
            "employee_id": forms.TextInput(attrs={
                "placeholder": "Example: STF001"
            }),

            "department": forms.TextInput(attrs={
                "placeholder": "Example: Electrical Maintenance"
            }),

            "phone_number": forms.TextInput(attrs={
                "placeholder": "Example: 9876543210"
            }),
        }