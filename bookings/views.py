from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from .models import Booking, SubEventBooking, CategoryBooking, Discount
from .forms import BookingForm, DiscountForm
from events.models import Event, SubEvent, Category
from utils.email_utils import (
    send_booking_confirmation,
    send_booking_approved,
    send_booking_rejected,
    send_booking_cancelled
)
import datetime

@login_required
def create_booking(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)

    # Check if user profile is complete
    profile = request.user.profile
    if not profile.mobile_number or not profile.address:
        messages.error(request, 'Please complete your profile with phone number and address before booking.')
        return redirect('edit_profile')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Create booking
            booking = form.save(commit=False)
            booking.user = request.user
            booking.event = event
            booking.booking_date = form.cleaned_data.get('booking_date')
            booking.guest_count = form.cleaned_data.get('guest_count')

            # Set initial prices to 0
            booking.total_price = 0
            booking.final_price = 0
            booking.save()

            # Process selected sub-events
            selected_sub_events = request.POST.getlist('sub_events')
            for sub_event_id in selected_sub_events:
                sub_event = get_object_or_404(SubEvent, id=sub_event_id, event=event)
                sub_event_booking = SubEventBooking.objects.create(
                    booking=booking,
                    sub_event=sub_event
                )

                # Process selected categories for this sub-event
                selected_categories = request.POST.getlist(f'categories_{sub_event_id}')
                for category_id in selected_categories:
                    category = get_object_or_404(Category, id=category_id, sub_event=sub_event)
                    CategoryBooking.objects.create(
                        sub_event_booking=sub_event_booking,
                        category=category
                    )

            # Apply discount if provided
            discount_code = request.POST.get('discount_code')
            if discount_code:
                try:
                    discount = Discount.objects.get(
                        code=discount_code,
                        is_active=True,
                        valid_from__lte=timezone.now(),
                        valid_to__gte=timezone.now()
                    )
                    booking.discount = discount
                    booking.save()
                except Discount.DoesNotExist:
                    pass

            # Calculate final price
            booking.calculate_total_price()
            booking.save()

            # Send booking confirmation email
            send_booking_confirmation(booking, request)

            messages.success(request, 'Your booking has been submitted successfully! A confirmation email has been sent to your email address.')
            return redirect('bookings:booking_detail', booking_id=booking.booking_id)
    else:
        form = BookingForm()

    # Get all sub-events and their categories
    sub_events = event.sub_events.all()

    context = {
        'form': form,
        'event': event,
        'sub_events': sub_events
    }

    return render(request, 'bookings/create_booking.html', context)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'bookings': bookings
    }

    return render(request, 'bookings/my_bookings.html', context)

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    sub_event_bookings = booking.sub_event_bookings.all()

    context = {
        'booking': booking,
        'sub_event_bookings': sub_event_bookings
    }

    return render(request, 'bookings/booking_detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    # Only allow cancellation if booking is pending
    if booking.status != 'pending':
        messages.error(request, 'You can only cancel pending bookings.')
        return redirect('bookings:booking_detail', booking_id=booking_id)

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()

        # Send booking cancelled email
        email_sent = send_booking_cancelled(booking, request)

        if email_sent:
            messages.success(request, 'Your booking has been cancelled. A confirmation email has been sent to your email address.')
        else:
            messages.success(request, 'Your booking has been cancelled.')

        return redirect('bookings:my_bookings')

    context = {
        'booking': booking
    }

    return render(request, 'bookings/cancel_booking.html', context)

# Manager views
@login_required
def manager_bookings(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    # Get all events created by this manager for the filter dropdown
    events = Event.objects.filter(created_by=request.user)

    # Get all bookings for events created by this manager
    bookings = Booking.objects.filter(event__created_by=request.user).order_by('-created_at')

    # Apply filters
    # Filter by event if provided
    event_id = request.GET.get('event')
    if event_id:
        bookings = bookings.filter(event_id=event_id)

    # Filter by status if provided
    status = request.GET.get('status')
    if status and status in dict(Booking.STATUS_CHOICES):
        bookings = bookings.filter(status=status)

    # Filter by date range if provided
    date_from = request.GET.get('date_from')
    if date_from:
        bookings = bookings.filter(booking_date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        bookings = bookings.filter(booking_date__lte=date_to)

    # Calculate statistics
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()
    approved_bookings = bookings.filter(status='approved').count()

    # Calculate total revenue from approved bookings
    from django.db.models import Sum
    total_revenue = bookings.filter(status='approved').aggregate(Sum('final_price'))['final_price__sum'] or 0

    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(bookings, 10)  # Show 10 bookings per page
    page = request.GET.get('page')

    try:
        paginated_bookings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        paginated_bookings = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        paginated_bookings = paginator.page(paginator.num_pages)

    context = {
        'bookings': paginated_bookings,
        'events': events,
        'status_choices': Booking.STATUS_CHOICES,
        'current_status': status,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'total_revenue': total_revenue
    }

    return render(request, 'bookings/manager_bookings.html', context)

@login_required
def manager_booking_detail(request, booking_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    booking = get_object_or_404(Booking, booking_id=booking_id, event__created_by=request.user)
    sub_event_bookings = booking.sub_event_bookings.all()

    context = {
        'booking': booking,
        'sub_event_bookings': sub_event_bookings
    }

    return render(request, 'bookings/manager_booking_detail.html', context)

@login_required
def approve_booking(request, booking_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    booking = get_object_or_404(Booking, booking_id=booking_id, event__created_by=request.user)

    if booking.status != 'pending':
        messages.error(request, 'You can only approve pending bookings.')
        return redirect('bookings:manager_booking_detail', booking_id=booking_id)

    if request.method == 'POST':
        booking.status = 'approved'
        booking.save()

        # Send booking approved email
        email_sent = send_booking_approved(booking, request)

        if email_sent:
            messages.success(request, 'Booking has been approved and the customer has been notified via email.')
        else:
            messages.success(request, 'Booking has been approved, but there was an issue sending the email notification.')

        return redirect('bookings:manager_bookings')

    context = {
        'booking': booking
    }

    return render(request, 'bookings/approve_booking.html', context)

@login_required
def reject_booking(request, booking_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    booking = get_object_or_404(Booking, booking_id=booking_id, event__created_by=request.user)

    if booking.status != 'pending':
        messages.error(request, 'You can only reject pending bookings.')
        return redirect('bookings:manager_booking_detail', booking_id=booking_id)

    if request.method == 'POST':
        booking.status = 'rejected'
        booking.save()

        # Send booking rejected email
        email_sent = send_booking_rejected(booking, request)

        if email_sent:
            messages.success(request, 'Booking has been rejected and the customer has been notified via email.')
        else:
            messages.success(request, 'Booking has been rejected, but there was an issue sending the email notification.')

        return redirect('bookings:manager_bookings')

    context = {
        'booking': booking
    }

    return render(request, 'bookings/reject_booking.html', context)

# Discount views
@login_required
def discount_list(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    discounts = Discount.objects.all().order_by('-created_at')

    context = {
        'discounts': discounts
    }

    return render(request, 'bookings/discount_list.html', context)

@login_required
def create_discount(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    if request.method == 'POST':
        # Check if we're coming from the modal form or the full form
        if 'discount_percent' in request.POST:
            # Coming from the modal form in discount_list.html
            try:
                # Extract data from the modal form
                code = request.POST.get('code')
                name = request.POST.get('name', '')  # This field isn't in the model, but is in the form
                percentage = float(request.POST.get('discount_percent'))
                description = request.POST.get('description', '')

                # Parse the valid_until date
                valid_until_str = request.POST.get('valid_until')
                valid_until = datetime.datetime.strptime(valid_until_str, '%Y-%m-%d').date()

                # Set valid_from to now and valid_to to end of the valid_until day
                valid_from = timezone.now()
                valid_to = datetime.datetime.combine(
                    valid_until,
                    datetime.time(23, 59, 59)
                ).replace(tzinfo=timezone.get_current_timezone())

                # Create the discount
                discount = Discount(
                    code=code,
                    description=description,
                    percentage=percentage,
                    is_active=True,
                    valid_from=valid_from,
                    valid_to=valid_to
                )
                discount.save()

                messages.success(request, f'Discount code {code} created successfully!')
                return redirect('discount_list')
            except Exception as e:
                messages.error(request, f'Error creating discount: {str(e)}')
                return redirect('discount_list')
        else:
            # Coming from the full form in discount_form.html
            form = DiscountForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Discount created successfully!')
                return redirect('discount_list')
    else:
        form = DiscountForm()

    context = {
        'form': form,
        'title': 'Create Discount'
    }

    return render(request, 'bookings/discount_form.html', context)

@login_required
def edit_discount(request, discount_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    discount = get_object_or_404(Discount, id=discount_id)

    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount updated successfully!')
            return redirect('discount_list')
    else:
        form = DiscountForm(instance=discount)

    context = {
        'form': form,
        'discount': discount,
        'title': 'Edit Discount'
    }

    return render(request, 'bookings/discount_form.html', context)

@login_required
def delete_discount(request, discount_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    discount = get_object_or_404(Discount, id=discount_id)

    if request.method == 'POST':
        discount.delete()
        messages.success(request, 'Discount deleted successfully!')
        return redirect('discount_list')

    context = {
        'discount': discount
    }

    return render(request, 'bookings/delete_discount.html', context)

# Apply discount via AJAX
def apply_discount(request):
    if request.method == 'POST':
        discount_code = request.POST.get('discount_code')
        if not discount_code:
            return JsonResponse({
                'valid': False,
                'message': 'No discount code provided.'
            })

        # Log the received discount code for debugging
        print(f"Received discount code: {discount_code}")

        # Get all discounts for debugging
        all_discounts = Discount.objects.all()
        print(f"All discounts in database: {[d.code for d in all_discounts]}")

        # IMPORTANT: Normalize the discount code (trim whitespace and convert to uppercase)
        normalized_code = discount_code.strip().upper()
        print(f"Normalized discount code: {normalized_code}")

        # First try with exact match (case-insensitive)
        discounts = Discount.objects.filter(code__iexact=normalized_code)

        if not discounts.exists():
            print(f"No discount found with code: {normalized_code}")
            return JsonResponse({
                'valid': False,
                'message': 'Invalid discount code.'
            })

        # Get the first matching discount
        discount = discounts.first()
        print(f"Found discount: {discount.code} - {discount.percentage}%")

        # Check if the discount is active and valid
        now = timezone.now()
        print(f"Current time: {now}")
        print(f"Discount valid from: {discount.valid_from}")
        print(f"Discount valid to: {discount.valid_to}")
        print(f"Discount is active: {discount.is_active}")

        if not discount.is_active:
            return JsonResponse({
                'valid': False,
                'message': 'This discount code is not active.'
            })
        elif discount.valid_from > now:
            return JsonResponse({
                'valid': False,
                'message': 'This discount code is not yet valid.'
            })
        elif discount.valid_to < now:
            return JsonResponse({
                'valid': False,
                'message': 'This discount code has expired.'
            })

        # If we get here, the discount is valid
        print(f"Discount is valid, returning percentage: {float(discount.percentage)}")
        return JsonResponse({
            'valid': True,
            'percentage': float(discount.percentage),
            'code': discount.code
        })

    return JsonResponse({'valid': False, 'message': 'Invalid request.'})