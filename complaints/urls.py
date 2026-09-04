from django.urls import path
from . import views


urlpatterns = [

    # =====================================================
    # GENERAL / DASHBOARDS
    # =====================================================

    path(
        "",
        views.dashboard,
        name="complaints_home"
    ),

    path(
        "student-dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "staff-dashboard/",
        views.staff_dashboard,
        name="staff_dashboard"
    ),

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    # =====================================================
    # STUDENT COMPLAINTS
    # =====================================================

    path(
        "submit/",
        views.submit_complaint,
        name="submit_complaint"
    ),

    path(
        "my-complaints/",
        views.my_complaints,
        name="my_complaints"
    ),

    path(
        "complaint/<int:pk>/",
        views.complaint_detail,
        name="complaint_detail"
    ),


    # =====================================================
    # ADMIN — COMPLAINT MANAGEMENT
    # =====================================================

    path(
        "admin/assign/<int:complaint_id>/",
        views.assign_complaint,
        name="assign_complaint"
    ),


    # =====================================================
    # STAFF — COMPLAINT MANAGEMENT
    # =====================================================

    path(
        "staff/start/<int:complaint_id>/",
        views.start_complaint,
        name="start_complaint"
    ),

    path(
        "staff/resolve/<int:complaint_id>/",
        views.resolve_complaint,
        name="resolve_complaint"
    ),


    # =====================================================
    # ADMIN — ANALYTICS
    # =====================================================

    path(
        "admin-analytics/",
        views.admin_analytics,
        name="admin_analytics"
    ),


    # =====================================================
    # ADMIN — USER MANAGEMENT
    # =====================================================

    path(
        "admin/users/",
        views.admin_users,
        name="admin_users"
    ),

    path(
        "admin/users/add/",
        views.admin_create_user,
        name="admin_create_user"
    ),

    path(
        "admin/users/<int:user_id>/edit/",
        views.admin_edit_user,
        name="admin_edit_user"
    ),

    path(
        "admin/users/<int:user_id>/delete/",
        views.admin_delete_user,
        name="admin_delete_user"
    ),


    # =====================================================
    # ADMIN — STAFF MANAGEMENT
    # =====================================================

    path(
        "admin/staff/",
        views.admin_staff,
        name="admin_staff"
    ),

    path(
        "admin/staff/add/",
        views.admin_create_staff,
        name="admin_create_staff"
    ),

    path(
        "admin/staff/<int:profile_id>/edit/",
        views.admin_edit_staff,
        name="admin_edit_staff"
    ),

    path(
        "admin/staff/<int:profile_id>/verify/",
        views.admin_verify_staff,
        name="admin_verify_staff"
    ),

]