from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q, F
from django.http import JsonResponse
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
            email_sent = send_welcome_email(user)

            if email_sent:
                messages.success(request, f'Account created for {username}! A welcome email has been sent to your email address. You can now log in.')
            else:
                messages.success(request, f'Account created for {username}! You can now log in.')

            return redirect('login')
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
        return redirect('manager_dashboard')

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
            return redirect('profile')
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
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    # Get current date and time
    now = timezone.now()

    # Get all bookings
    all_bookings = Booking.objects.all()

    # Get bookings for the current month
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
    current_month_bookings = all_bookings.filter(created_at__gte=current_month_start, created_at__lt=next_month_start)

    # Get approved and pending bookings
    approved_bookings = current_month_bookings.filter(status='approved')
    pending_bookings = current_month_bookings.filter(status='pending')

    # Calculate revenue
    total_revenue = approved_bookings.aggregate(total=Sum('total_price'))['total'] or 0

    # Get average rating
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0

    # Get booking counts by month for the last 6 months
    months_data = []
    for i in range(5, -1, -1):
        month_date = (now - timedelta(days=30*i)).replace(day=1)
        month_name = month_date.strftime('%B')
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = (month_date + timedelta(days=32)).replace(day=1)
        else:
            month_end = now

        month_approved = all_bookings.filter(created_at__gte=month_start, created_at__lt=month_end, status='approved').count()
        month_rejected = all_bookings.filter(created_at__gte=month_start, created_at__lt=month_end, status='rejected').count()

        months_data.append({
            'month': month_name,
            'approved': month_approved,
            'rejected': month_rejected
        })

    # Get top events by bookings
    top_events = Event.objects.annotate(booking_count=Count('bookings')).order_by('-booking_count')[:5]

    # Get recent bookings
    recent_bookings = all_bookings.order_by('-created_at')[:10]

    context = {
        'total_bookings': all_bookings.count(),
        'approved_bookings': all_bookings.filter(status='approved').count(),
        'pending_bookings': all_bookings.filter(status='pending').count(),
        'total_revenue': total_revenue,
        'avg_rating': avg_rating,
        'months_data': json.dumps(months_data),
        'top_events': top_events,
        'recent_bookings': recent_bookings,
    }

    return render(request, 'accounts/manager_dashboard.html', context)

@login_required
def booking_analytics(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get all bookings
    bookings = Booking.objects.all()

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