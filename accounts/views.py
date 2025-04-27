from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q, F
from django.http import JsonResponse
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from datetime import timedelta
import json
import calendar
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from utils.email_utils import send_welcome_email
from bookings.models import Booking
from events.models import Event, Review

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # Send welcome email
            email_sent = send_welcome_email(user, request)

            if email_sent:
                messages.success(request, f'Account created for {username}! A welcome email has been sent to your email address. You can now log in.')
            else:
                messages.success(request, f'Account created for {username}! You can now log in.')

            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def dashboard(request):
    # Redirect managers to manager dashboard
    if request.user.profile.is_manager:
        # Redirect to the events manager dashboard instead of accounts manager dashboard
        return redirect('events:manager_dashboard')

    # Get user's bookings
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')

    # Count bookings by status
    pending_count = user_bookings.filter(status='pending').count()
    approved_count = user_bookings.filter(status='approved').count()

    context = {
        'bookings': user_bookings,
        'pending_count': pending_count,
        'approved_count': approved_count
    }

    return render(request, 'accounts/dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'accounts/edit_profile.html', context)

@login_required
def manager_dashboard(request):
    # This view is deprecated - redirect to the events manager dashboard
    return redirect('events:manager_dashboard')


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view to use our custom email template
    """
    template_name = 'accounts/password_reset.html'
    email_template_name = 'emails/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        """
        Add site_url to the context for the email template
        """
        # Get the protocol (http or https)
        protocol = 'https' if self.request.is_secure() else 'http'

        # Get the host (domain)
        host = self.request.get_host()

        # Construct the full site URL
        site_url = f"{protocol}://{host}"

        # Add site_url to the context
        self.extra_email_context = {
            'site_url': site_url
        }

        return super().form_valid(form)

@login_required
def booking_analytics(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    try:
        # Get all bookings
        bookings = Booking.objects.all()
    except Exception as e:
        # Log the error and return a friendly error message
        print(f"Error in booking_analytics: {e}")
        return JsonResponse({'error': 'An error occurred while fetching booking data'}, status=500)

    # Get booking data by day of week
    weekday_data = [0] * 7  # Initialize counts for each day of the week
    for booking in bookings:
        weekday = booking.created_at.weekday()
        weekday_data[weekday] += 1

    # Get booking data by hour of day
    hourly_data = [0] * 24  # Initialize counts for each hour
    for booking in bookings:
        hour = booking.created_at.hour
        hourly_data[hour] += 1

    # Get booking status distribution
    status_data = {
        'approved': bookings.filter(status='approved').count(),
        'pending': bookings.filter(status='pending').count(),
        'rejected': bookings.filter(status='rejected').count(),
        'cancelled': bookings.filter(status='cancelled').count(),
    }

    # Get revenue by month for the current year
    current_year = timezone.now().year
    monthly_revenue = [0] * 12  # Initialize revenue for each month

    for month in range(1, 13):
        month_revenue = bookings.filter(
            created_at__year=current_year,
            created_at__month=month,
            status='approved'
        ).aggregate(total=Sum('total_price'))['total'] or 0

        monthly_revenue[month-1] = float(month_revenue)

    return JsonResponse({
        'weekday_data': {
            'labels': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'data': weekday_data
        },
        'hourly_data': {
            'labels': list(range(24)),
            'data': hourly_data
        },
        'status_data': status_data,
        'monthly_revenue': {
            'labels': list(calendar.month_name)[1:],
            'data': monthly_revenue
        }
    })