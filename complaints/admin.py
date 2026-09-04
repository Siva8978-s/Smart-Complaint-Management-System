from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, Complaint


# =========================================================
# PROFILE INLINE
# =========================================================

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "User Role"


# =========================================================
# CUSTOM USER ADMIN
# =========================================================

class CustomUserAdmin(UserAdmin):

    inlines = [ProfileInline]

    list_display = (
        "username",
        "email",
        "get_role",
        "is_staff",
        "is_active",
    )

    def get_role(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.role
        return "No Profile"

    get_role.short_description = "Role"


# Remove Django's default User admin
admin.site.unregister(User)

# Register User with our customized admin
admin.site.register(User, CustomUserAdmin)


# =========================================================
# PROFILE ADMIN
# =========================================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
        "employee_id",
        "department",
        "phone_number",
        "is_verified",
    )

    list_filter = (
        "role",
        "is_verified",
        "department",
    )

    search_fields = (
        "user__username",
        "employee_id",
        "department",
        "phone_number",
    )
# =========================================================
# COMPLAINT ADMIN
# =========================================================

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "priority",
        "status",
        "submitted_by",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "priority",
        "status",
        "category",
    )

    search_fields = (
        "title",
        "description",
        "location",
        "submitted_by__username",
    )