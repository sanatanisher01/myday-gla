from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Event, Review
from bookings.models import Booking
import json

@login_required
def manager_dashboard(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    try:
        # Get events created by this manager
        events = Event.objects.filter(created_by=request.user)

        # Get bookings for these events
        bookings = Booking.objects.filter(event__in=events)
    except Exception as e:
        # Log the error and show a friendly message
        print(f"Error in manager_dashboard: {e}")
        messages.error(request, 'There was an error loading your dashboard. Please try again later.')
        return redirect('events:home')

    # Calculate statistics
    total_events = events.count()
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()
    approved_bookings = bookings.filter(status='approved').count()

    # Calculate total revenue
    total_revenue = bookings.filter(status='approved').aggregate(
        total=Sum('final_price')
    )['total'] or 0

    # Get recent bookings
    recent_bookings = bookings.order_by('-created_at')[:10]

    # Get recent events
    recent_events = events.order_by('-created_at')[:5]

    # Generate monthly booking statistics for the chart using real data
    now = timezone.now()
    monthly_approved = [0] * 12
    monthly_pending = [0] * 12
    monthly_rejected = [0] * 12

    # Get all bookings for the last 12 months
    year_ago = now - timedelta(days=365)
    yearly_bookings = bookings.filter(created_at__gte=year_ago)

    # Prepare monthly data
    for i in range(12):
        # Calculate the month (starting from 11 months ago to current month)
        month_date = now - timedelta(days=30 * (11 - i))
        year = month_date.year

        # Get bookings for this month
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_date.month == 12:
            month_end = month_date.replace(year=year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        month_end = month_end.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Count bookings by status for this month
        month_bookings = yearly_bookings.filter(created_at__gte=month_start, created_at__lte=month_end)
        monthly_approved[i] = month_bookings.filter(status='approved').count()
        monthly_pending[i] = month_bookings.filter(status='pending').count()
        monthly_rejected[i] = month_bookings.filter(status='rejected').count()

    # Calculate performance metrics based on real data
    # Conversion rate: Percentage of approved bookings out of total bookings
    conversion_rate = 0
    if total_bookings > 0:
        conversion_rate = int((approved_bookings / total_bookings) * 100)

    # Satisfaction rate: Average rating from reviews (scaled to percentage)
    avg_rating = 0
    review_count = 0
    for event in events:
        event_reviews = event.reviews.all()
        if event_reviews.exists():
            avg_rating += event_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            review_count += 1

    satisfaction_rate = 0
    if review_count > 0:
        # Convert average rating (1-5) to percentage (0-100)
        satisfaction_rate = int((avg_rating / review_count / 5) * 100)

    # Revenue growth: Compare current month revenue to previous month
    current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month = (current_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    current_month_end = now

    current_month_revenue = bookings.filter(
        created_at__gte=current_month,
        created_at__lte=current_month_end,
        status='approved'
    ).aggregate(total=Sum('final_price'))['total'] or 0

    prev_month_revenue = bookings.filter(
        created_at__gte=prev_month,
        created_at__lt=current_month,
        status='approved'
    ).aggregate(total=Sum('final_price'))['total'] or 0

    revenue_growth = 0
    if prev_month_revenue > 0:
        revenue_growth = int(((current_month_revenue - prev_month_revenue) / prev_month_revenue) * 100)
    elif current_month_revenue > 0:
        revenue_growth = 100  # If there was no revenue last month but there is this month

    context = {
        'total_events': total_events,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_events': recent_events,
        'monthly_approved': json.dumps(monthly_approved),
        'monthly_pending': json.dumps(monthly_pending),
        'monthly_rejected': json.dumps(monthly_rejected),
        'conversion_rate': conversion_rate,
        'satisfaction_rate': satisfaction_rate,
        'revenue_growth': revenue_growth,
    }

    return render(request, 'manager/dashboard.html', context)

@login_required
def manager_events(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    events = Event.objects.filter(created_by=request.user).annotate(
        booking_count=Count('bookings'),
        sub_event_count=Count('sub_events')
    ).order_by('-created_at')

    context = {
        'events': events
    }

    return render(request, 'manager/events.html', context)

@login_required
def manager_event_detail(request, slug):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    event = get_object_or_404(Event, slug=slug, created_by=request.user)
    sub_events = event.sub_events.all()
    bookings = event.bookings.all().order_by('-created_at')

    # Calculate statistics
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()
    approved_bookings = bookings.filter(status='approved').count()
    rejected_bookings = bookings.filter(status='rejected').count()

    # Calculate revenue
    total_revenue = bookings.filter(status='approved').aggregate(
        total=Sum('final_price')
    )['total'] or 0

    # Calculate average rating
    avg_rating = event.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    # Get booking data by month for the chart
    # Get the last 12 months
    now = timezone.now()
    months = []
    booking_counts = []
    booking_revenue = []

    for i in range(11, -1, -1):
        # Calculate the month
        month_date = now - timedelta(days=30 * i)
        month_name = month_date.strftime('%b')
        months.append(month_name)

        # Get bookings for this month
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            next_month = month_date.replace(day=28) + timedelta(days=4)
            month_end = next_month.replace(day=1) - timedelta(days=1)
            month_end = month_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            month_end = now

        # Count bookings in this month
        month_bookings = bookings.filter(created_at__gte=month_start, created_at__lte=month_end)
        booking_counts.append(month_bookings.count())

        # Calculate revenue for this month
        month_revenue = month_bookings.filter(status='approved').aggregate(
            total=Sum('final_price')
        )['total'] or 0
        booking_revenue.append(float(month_revenue))

    context = {
        'event': event,
        'sub_events': sub_events,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings,
        'total_revenue': total_revenue,
        'avg_rating': avg_rating,
        'booking_months': json.dumps(months),
        'booking_counts': json.dumps(booking_counts),
        'booking_revenue': json.dumps(booking_revenue)
    }

    return render(request, 'manager/event_detail.html', context)
