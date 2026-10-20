from .forms import ComplaintForm, AssignmentForm, ResolutionForm
from .models import Complaint, Profile
from django.contrib.auth.models import User


from django.db.models import Count, Q, Case, When, IntegerField

from functools import wraps

from .models import Complaint, Comment
from .forms import ComplaintForm, AssignmentForm, ResolutionForm, CommentForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import (
    ComplaintForm,
    AssignmentForm,
    ResolutionForm,
    CommentForm,
    UserCreateForm,
    UserEditForm,
    StaffCreateForm,
    StaffEditForm,
)

from .models import Complaint, Profile

def role_required(*allowed_roles):
    """
    Allows access only to users whose Profile role
    matches one of the allowed roles.
    """

    def decorator(view_func):

        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):

            if not hasattr(request.user, "profile"):
                return redirect("login")

            if request.user.profile.role not in allowed_roles:
                return render(
                    request,
                    "complaints/access_denied.html",
                    status=403
                )

            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator

def home(request):
    return render(request, "complaints/home.html")

@role_required("student")
def submit_complaint(request):
    """Handles both showing the empty form (GET) and processing
    a submitted form (POST)."""
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)  # don't save yet
            complaint.submitted_by = request.user  # attach logged-in user
            complaint.save()  # NOW it saves - triggers the classifier
            return redirect("my_complaints")
    else:
        form = ComplaintForm()

    return render(request, "complaints/submit_complaint.html", {"form": form})


@role_required("student")
def my_complaints(request):
    """Shows the logged-in user only THEIR complaints and status -
    this is your 'track complaint status' feature."""
    complaints = Complaint.objects.filter(submitted_by=request.user).order_by("-created_at")
    return render(request, "complaints/my_complaints.html", {"complaints": complaints})

@role_required("student")
def student_dashboard(request):
    complaints = Complaint.objects.filter(
        submitted_by=request.user
    ).order_by("-created_at")

    total = complaints.count()
    pending = complaints.filter(
        status__in=["submitted", "assigned"]
    ).count()
    in_progress = complaints.filter(
        status="in_progress"
    ).count()
    resolved = complaints.filter(
        status="resolved"
    ).count()

    context = {
        "complaints": complaints[:5],
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
    }

    return render(
        request,
        "complaints/student_dashboard.html",
        context
    )

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    role = profile.role

    if role == "staff":
        return redirect("staff_dashboard")

    elif role == "admin":
        return redirect("admin_dashboard")

    return redirect("student_dashboard")

@role_required("staff")
def staff_dashboard(request):
    complaints = Complaint.objects.filter(
        assigned_to=request.user
    ).select_related(
        "submitted_by"
    ).order_by(
        "-created_at"
    )

    total = complaints.count()

    assigned = complaints.filter(
        status="assigned"
    ).count()

    in_progress = complaints.filter(
        status="in_progress"
    ).count()

    resolved = complaints.filter(
        status="resolved"
    ).count()

    context = {
        "complaints": complaints,
        "total": total,
        "assigned": assigned,
        "in_progress": in_progress,
        "resolved": resolved,
    }

    return render(
        request,
        "complaints/staff_dashboard.html",
        context
    )

@role_required("admin")
def admin_dashboard(request):

    search_query = request.GET.get("search", "").strip()

    priority_filter = request.GET.get("priority", "").strip()

    status_filter = request.GET.get("status", "").strip()


    complaints = Complaint.objects.select_related(
        "submitted_by",
        "assigned_to"
    )


    # Search

    if search_query:

        complaints = complaints.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(category__icontains=search_query)
            | Q(submitted_by__username__icontains=search_query)
        )


    # Priority filter

    if priority_filter:

        complaints = complaints.filter(
            priority=priority_filter
        )


    # Status filter

    if status_filter:

        complaints = complaints.filter(
            status=status_filter
        )


    # Priority ordering

    complaints = complaints.annotate(

        priority_order=Case(

            When(priority="HIGH", then=1),

            When(priority="MEDIUM", then=2),

            When(priority="LOW", then=3),

            default=4,

            output_field=IntegerField(),

        )

    ).order_by(
        "priority_order",
        "-created_at"
    )


    return render(
        request,
        "complaints/admin_dashboard.html",
        {
            "complaints": complaints,
            "search_query": search_query,
            "priority_filter": priority_filter,
            "status_filter": status_filter,
        }
    )


@role_required("admin")
def assign_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=complaint)

        if form.is_valid():
            if not form.cleaned_data.get("assigned_to"):
                form.add_error("assigned_to", "Please select a staff member to assign.")
            else:
                complaint = form.save(commit=False)
                complaint.status = "assigned"
                complaint.save()
                messages.success(request, f"Complaint assigned to {complaint.assigned_to.username} successfully.")
                return redirect("admin_dashboard")

    else:
        form = AssignmentForm(instance=complaint)

    has_verified_staff = form.fields["assigned_to"].queryset.exists()

    return render(
        request,
        "complaints/assign_complaint.html",
        {
            "form": form,
            "complaint": complaint,
            "has_verified_staff": has_verified_staff,
        }
    )

@role_required("staff")
def start_complaint(request, complaint_id):
    complaint = Complaint.objects.get(
        id=complaint_id,
        assigned_to=request.user
    )

    if request.method == "POST":
        complaint.status = "in_progress"
        complaint.save()

    return redirect("staff_dashboard")

@role_required("staff")
def resolve_complaint(request, complaint_id):
    complaint = get_object_or_404(
        Complaint,
        id=complaint_id,
        assigned_to=request.user
    )

    if request.method == "POST":
        form = ResolutionForm(request.POST)

        if form.is_valid():
            complaint.resolution_remarks = form.cleaned_data["remarks"]
            complaint.status = "resolved"
            complaint.save()

            messages.success(request, f"Task '{complaint.title}' marked as resolved successfully.")
            return redirect("staff_dashboard")

    else:
        form = ResolutionForm()

    return render(
        request,
        "complaints/resolve_complaint.html",
        {
            "complaint": complaint,
            "form": form,
        }
    )

@role_required("admin")
def admin_analytics(request):

    total_complaints = Complaint.objects.count()

    submitted_count = Complaint.objects.filter(
        status="submitted"
    ).count()

    assigned_count = Complaint.objects.filter(
        status="assigned"
    ).count()

    in_progress_count = Complaint.objects.filter(
        status="in_progress"
    ).count()

    resolved_count = Complaint.objects.filter(
        status="resolved"
    ).count()


    # Priority statistics

    high_count = Complaint.objects.filter(
        priority="HIGH"
    ).count()

    medium_count = Complaint.objects.filter(
        priority="MEDIUM"
    ).count()

    low_count = Complaint.objects.filter(
        priority="LOW"
    ).count()


    # Category statistics

    category_data = (
        Complaint.objects
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total")
    )


    context = {
        "total_complaints": total_complaints,

        "submitted_count": submitted_count,
        "assigned_count": assigned_count,
        "in_progress_count": in_progress_count,
        "resolved_count": resolved_count,

        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,

        "category_data": category_data,
    }

    return render(
        request,
        "complaints/admin_analytics.html",
        context
    )


complaints = Complaint.objects.select_related(
    "submitted_by",
    "assigned_to"
).annotate(
    priority_order=Case(
        When(priority="HIGH", then=1),
        When(priority="MEDIUM", then=2),
        When(priority="LOW", then=3),
        default=4,
        output_field=IntegerField(),
    )
).order_by(
    "priority_order",
    "-created_at"
)


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

# Make sure you import Comment and CommentForm at the top:


@login_required
def complaint_detail(request, pk):
    # Fetch the specific complaint
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Security Check: Only allow the student who submitted it, the assigned staff, or an admin to view it
    is_authorized = (
        request.user == complaint.submitted_by or 
        request.user == complaint.assigned_to or 
        request.user.profile.role == 'admin'
    )
    
    if not is_authorized:
        return render(request, 'complaints/access_denied.html')

    # Fetch all comments for this complaint, ordered by oldest to newest
    comments = complaint.comments.all().order_by('created_at')
    
    # Handle the comment form submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.complaint = complaint
            new_comment.author = request.user # The person logged in is the author
            new_comment.save()
            # Reload the page to show the new comment
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = CommentForm()
        
    context = {
        'complaint': complaint,
        'comments': comments,
        'form': form
    }
    return render(request, 'complaints/complaint_detail.html', context)


@login_required
@role_required("admin")
def admin_users(request):

    users = User.objects.select_related("profile").all().order_by("username")

    return render(
        request,
        "complaints/admin_users.html",
        {
            "users": users,
        }
    )


@login_required
@role_required("admin")
def admin_create_user(request):

    if request.method == "POST":

        form = UserCreateForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            password = form.cleaned_data["password"]
            role = form.cleaned_data["role"]

            user.set_password(password)
            user.save()

            Profile.objects.create(
                user=user,
                role=role
            )

            messages.success(
                request,
                f"User '{user.username}' created successfully."
            )

            return redirect("admin_users")

    else:

        form = UserCreateForm()

    return render(
        request,
        "complaints/admin_create_user.html",
        {
            "form": form,
        }
    )


@login_required
@role_required("admin")
def admin_edit_user(request, user_id):

    user = get_object_or_404(User, id=user_id)

    profile, created = Profile.objects.get_or_create(
        user=user
    )

    if request.method == "POST":

        form = UserEditForm(
            request.POST,
            instance=user
        )

        if form.is_valid():

            user = form.save()

            profile.role = form.cleaned_data["role"]
            profile.save()

            messages.success(
                request,
                f"User '{user.username}' updated successfully."
            )

            return redirect("admin_users")

    else:

        form = UserEditForm(
            instance=user,
            initial={
                "role": profile.role
            }
        )

    return render(
        request,
        "complaints/admin_edit_user.html",
        {
            "form": form,
            "user_obj": user,
        }
    )


@login_required
@role_required("admin")
def admin_delete_user(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if user == request.user:

        messages.error(
            request,
            "You cannot delete your own admin account."
        )

        return redirect("admin_users")

    if request.method == "POST":

        username = user.username

        user.delete()

        messages.success(
            request,
            f"User '{username}' deleted successfully."
        )

        return redirect("admin_users")

    return render(
        request,
        "complaints/admin_delete_user.html",
        {
            "user_obj": user,
        }
    )


@login_required
@role_required("admin")
def admin_staff(request):

    staff_profiles = Profile.objects.filter(
        role="staff"
    ).select_related("user").order_by("user__username")

    return render(
        request,
        "complaints/admin_staff.html",
        {
            "staff_profiles": staff_profiles,
        }
    )



@login_required
@role_required("admin")
def admin_create_staff(request):

    if request.method == "POST":

        form = StaffCreateForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]

            if User.objects.filter(username=username).exists():

                form.add_error(
                    "username",
                    "This username already exists."
                )

            else:

                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )

                profile = form.save(commit=False)

                profile.user = user
                profile.role = "staff"
                profile.save()

                messages.success(
                    request,
                    f"Staff '{username}' created successfully."
                )

                return redirect("admin_staff")

    else:

        form = StaffCreateForm()

    return render(
        request,
        "complaints/admin_create_staff.html",
        {
            "form": form,
        }
    )


@login_required
@role_required("admin")
def admin_edit_staff(request, profile_id):

    profile = get_object_or_404(
        Profile,
        id=profile_id,
        role="staff"
    )

    user = profile.user

    if request.method == "POST":

        form = StaffEditForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            # Username remains unchanged
            # because it is the account identifier.
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]

            user.save()

            # Save Profile information
            form.save()

            messages.success(
                request,
                f"Staff '{user.username}' updated successfully."
            )

            return redirect("admin_staff")

    else:

        form = StaffEditForm(
            instance=profile,
            initial={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            }
        )

    return render(
        request,
        "complaints/admin_edit_staff.html",
        {
            "form": form,
            "profile": profile,
        }
    )

@login_required
@role_required("admin")
def admin_verify_staff(request, profile_id):

    profile = get_object_or_404(
        Profile,
        id=profile_id,
        role="staff"
    )

    if request.method == "POST":

        profile.is_verified = not profile.is_verified
        profile.save()

        if profile.is_verified:

            messages.success(
                request,
                f"{profile.user.username} has been verified."
            )

        else:

            messages.warning(
                request,
                f"{profile.user.username} is no longer verified."
            )

    return redirect("admin_staff")






# =========================================================
# PUBLIC USER REGISTRATION (STUDENT)
# =========================================================

def register(request):
    from .forms import StudentRegisterForm

    if request.user.is_authenticated:
        return redirect("complaints_home")

    if request.method == "POST":
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            Profile.objects.create(user=user, role="student")
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("login")
    else:
        form = StudentRegisterForm()

    return render(request, "registration/register.html", {"form": form})
