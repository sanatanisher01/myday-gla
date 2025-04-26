from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Event(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    cover_photo = models.ImageField(upload_to='event_covers/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        # Base price from sub-events
        base_price = sum(sub_event.price for sub_event in self.sub_events.all())

        # Add minimum price for categories (assuming at least one category per sub-event if available)
        category_price = 0
        for sub_event in self.sub_events.all():
            if sub_event.categories.exists():
                # Add the price of the cheapest category for each sub-event
                min_category_price = min(category.price for category in sub_event.categories.all())
                category_price += min_category_price

        return base_price + category_price

class EventGallery(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='event_gallery/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=50, choices=[
        ('venue', 'Venue'),
        ('stage', 'Stage'),
        ('decor', 'Décor'),
        ('customs', 'Customs'),
        ('other', 'Other')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.name} - {self.category} Image"

class SubEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sub_events')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='sub_events/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.name} - {self.name}"

class SubEventGallery(models.Model):
    sub_event = models.ForeignKey(SubEvent, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='sub_event_gallery/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sub_event.name} Gallery Image"

class Category(models.Model):
    sub_event = models.ForeignKey(SubEvent, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sub_event.name} - {self.name}"

class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    # likes field removed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username}'s review for {self.event.name}"
