from django.db import models
from django.contrib.auth.models import User
from events.models import Event, SubEvent, Category
import uuid

class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.percentage}%"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    guest_count = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.booking_id} by {self.user.username}"

    def calculate_total_price(self):
        sub_event_bookings = self.sub_event_bookings.all()
        total = sum(seb.sub_event.price for seb in sub_event_bookings)

        # Add category prices
        for seb in sub_event_bookings:
            total += sum(cb.category.price for cb in seb.category_bookings.all())

        self.total_price = total

        # Apply discount if available
        if self.discount and self.discount.is_active:
            discount_amount = (self.total_price * self.discount.percentage) / 100
            self.final_price = self.total_price - discount_amount
        else:
            self.final_price = self.total_price

        return self.final_price

class SubEventBooking(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='sub_event_bookings')
    sub_event = models.ForeignKey(SubEvent, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.booking_id} - {self.sub_event.name}"

class CategoryBooking(models.Model):
    sub_event_booking = models.ForeignKey(SubEventBooking, on_delete=models.CASCADE, related_name='category_bookings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sub_event_booking.booking.booking_id} - {self.category.name}"
