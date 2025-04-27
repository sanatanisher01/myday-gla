from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt  # Removed with like functionality
from django.db.models import Avg, Count, Min, Max, Q
# from django.http import JsonResponse  # Removed with like functionality
from .models import Event, SubEvent, Category, EventGallery, Review
from .forms import EventForm, SubEventForm, CategoryForm, EventGalleryForm, ReviewForm

# Test like view removed

def home(request):
    # Try to get featured events and testimonials
    try:
        # Get featured events (for example, events with most bookings)
        featured_events = Event.objects.annotate(booking_count=Count('bookings')).order_by('-booking_count')[:3]

        # Get testimonials (top-rated reviews)
        testimonials = Review.objects.filter(rating__gte=4).order_by('-created_at')[:3]

        context = {
            'featured_events': featured_events,
            'testimonials': testimonials
        }
    except Exception as e:
        # If there's an error (e.g., database tables don't exist yet), use empty lists
        import sys
        print(f"Error in home view: {e}", file=sys.stderr)
        context = {
            'featured_events': [],
            'testimonials': [],
            'setup_mode': True,
            'error_message': str(e)
        }

    return render(request, 'events/home.html', context)

def event_list(request):
    # Start with all events
    events_query = Event.objects.all().annotate(
        avg_rating=Avg('reviews__rating'),
        sub_event_count=Count('sub_events', distinct=True)
    )

    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        events_query = events_query.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Apply price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        events_query = events_query.filter(sub_events__price__gte=min_price)
    if max_price:
        events_query = events_query.filter(sub_events__price__lte=max_price)

    # Apply rating filter
    min_rating = request.GET.get('min_rating')
    if min_rating:
        events_query = events_query.filter(avg_rating__gte=min_rating)

    # Apply sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'name':
        events_query = events_query.order_by('name')
    elif sort_by == 'price_low':
        events_query = events_query.order_by('sub_events__price')
    elif sort_by == 'price_high':
        events_query = events_query.order_by('-sub_events__price')
    elif sort_by == 'rating':
        events_query = events_query.order_by('-avg_rating')
    elif sort_by == 'newest':
        events_query = events_query.order_by('-created_at')

    # Get distinct events (to avoid duplicates from joins)
    events = events_query.distinct()

    # Get min and max prices for the filter
    price_range = SubEvent.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    context = {
        'events': events,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,
        'sort_by': sort_by,
        'price_range': price_range,
    }

    return render(request, 'events/event_list.html', context)

def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    sub_events = event.sub_events.all()
    gallery_images = event.gallery_images.all()
    reviews = event.reviews.all().order_by('-created_at')

    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        'event': event,
        'sub_events': sub_events,
        'gallery_images': gallery_images,
        'reviews': reviews,
        'avg_rating': avg_rating
    }

    return render(request, 'events/event_detail.html', context)

@login_required
def add_review(request, slug):
    event = get_object_or_404(Event, slug=slug)

    # Check if user has already reviewed this event
    existing_review = Review.objects.filter(event=event, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.event = event
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('event_detail', slug=slug)
    else:
        form = ReviewForm(instance=existing_review)

    context = {
        'form': form,
        'event': event,
        'existing_review': existing_review
    }

    return render(request, 'events/add_review.html', context)

# Manager views

@login_required
def create_event(request):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events:event_gallery', slug=event.slug)
    else:
        form = EventForm()

    context = {
        'form': form,
        'title': 'Create Event'
    }

    return render(request, 'events/event_form.html', context)

@login_required
def edit_event(request, slug):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    event = get_object_or_404(Event, slug=slug, created_by=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events:manager_events')
    else:
        form = EventForm(instance=event)

    context = {
        'form': form,
        'event': event,
        'title': 'Edit Event'
    }

    return render(request, 'events/event_form.html', context)

@login_required
def delete_event(request, slug):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    event = get_object_or_404(Event, slug=slug, created_by=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:manager_events')

    context = {
        'event': event
    }

    return render(request, 'events/delete_event.html', context)

# Sub-event views
@login_required
def create_sub_event(request, event_slug):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    event = get_object_or_404(Event, slug=event_slug, created_by=request.user)

    if request.method == 'POST':
        form = SubEventForm(request.POST, request.FILES)
        if form.is_valid():
            sub_event = form.save(commit=False)
            sub_event.event = event
            sub_event.save()
            messages.success(request, 'Sub-event created successfully!')
            return redirect('events:event_detail', slug=event_slug)
    else:
        form = SubEventForm()

    context = {
        'form': form,
        'event': event,
        'title': 'Create Sub-Event'
    }

    return render(request, 'events/sub_event_form.html', context)

@login_required
def edit_sub_event(request, sub_event_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    sub_event = get_object_or_404(SubEvent, id=sub_event_id, event__created_by=request.user)

    if request.method == 'POST':
        form = SubEventForm(request.POST, request.FILES, instance=sub_event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sub-event updated successfully!')
            return redirect('events:event_detail', slug=sub_event.event.slug)
    else:
        form = SubEventForm(instance=sub_event)

    context = {
        'form': form,
        'sub_event': sub_event,
        'event': sub_event.event,
        'title': 'Edit Sub-Event'
    }

    return render(request, 'events/sub_event_form.html', context)

@login_required
def delete_sub_event(request, sub_event_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    sub_event = get_object_or_404(SubEvent, id=sub_event_id, event__created_by=request.user)
    event_slug = sub_event.event.slug

    if request.method == 'POST':
        sub_event.delete()
        messages.success(request, 'Sub-event deleted successfully!')
        return redirect('events:event_detail', slug=event_slug)

    context = {
        'sub_event': sub_event,
        'event': sub_event.event
    }

    return render(request, 'events/delete_sub_event.html', context)

# Category views
@login_required
def create_category(request, sub_event_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    sub_event = get_object_or_404(SubEvent, id=sub_event_id, event__created_by=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.sub_event = sub_event
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('events:event_detail', slug=sub_event.event.slug)
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'sub_event': sub_event,
        'event': sub_event.event,
        'title': 'Create Category'
    }

    return render(request, 'events/category_form.html', context)

@login_required
def edit_category(request, category_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    category = get_object_or_404(Category, id=category_id, sub_event__event__created_by=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('events:event_detail', slug=category.sub_event.event.slug)
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'sub_event': category.sub_event,
        'event': category.sub_event.event,
        'title': 'Edit Category'
    }

    return render(request, 'events/category_form.html', context)

@login_required
def delete_category(request, category_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    category = get_object_or_404(Category, id=category_id, sub_event__event__created_by=request.user)
    event_slug = category.sub_event.event.slug

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('events:event_detail', slug=event_slug)

    context = {
        'category': category,
        'sub_event': category.sub_event,
        'event': category.sub_event.event
    }

    return render(request, 'events/delete_category.html', context)

# Gallery views
@login_required
def event_gallery(request, slug):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    event = get_object_or_404(Event, slug=slug, created_by=request.user)
    gallery_images = event.gallery_images.all()

    context = {
        'event': event,
        'gallery_images': gallery_images
    }

    return render(request, 'events/event_gallery.html', context)

@login_required
def add_event_image(request, slug):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    event = get_object_or_404(Event, slug=slug, created_by=request.user)

    if request.method == 'POST':
        form = EventGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_image = form.save(commit=False)
            gallery_image.event = event
            gallery_image.save()
            messages.success(request, 'Image added to gallery successfully!')
            return redirect('events:event_gallery', slug=slug)
    else:
        form = EventGalleryForm()

    context = {
        'form': form,
        'event': event,
        'title': 'Add Gallery Image'
    }

    return render(request, 'events/gallery_form.html', context)

@login_required
def delete_event_image(request, image_id):
    # Check if user is a manager
    if not request.user.profile.is_manager:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('events:home')

    image = get_object_or_404(EventGallery, id=image_id, event__created_by=request.user)
    event_slug = image.event.slug

    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('events:event_gallery', slug=event_slug)

    context = {
        'image': image,
        'event': image.event
    }

    return render(request, 'events/delete_image.html', context)

# Like functionality removed