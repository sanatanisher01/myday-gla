from django.contrib import admin
from .models import Booking, SubEventBooking, CategoryBooking, Discount

class SubEventBookingInline(admin.TabularInline):
    model = SubEventBooking
    extra = 0
    readonly_fields = ('sub_event',)

class CategoryBookingInline(admin.TabularInline):
    model = CategoryBooking
    extra = 0
    readonly_fields = ('category',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'event', 'status', 'total_price', 'final_price', 'created_at')
    list_filter = ('status', 'created_at', 'event')
    search_fields = ('booking_id', 'user__username', 'event__name')
    readonly_fields = ('booking_id', 'created_at', 'updated_at')
    inlines = [SubEventBookingInline]
    fieldsets = (
        (None, {
            'fields': ('booking_id', 'user', 'event', 'status')
        }),
        ('Booking Details', {
            'fields': ('guest_count', 'booking_date', 'discount')
        }),
        ('Pricing', {
            'fields': ('total_price', 'final_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(SubEventBooking)
class SubEventBookingAdmin(admin.ModelAdmin):
    list_display = ('booking', 'sub_event', 'created_at')
    list_filter = ('booking__status', 'created_at')
    search_fields = ('booking__booking_id', 'sub_event__name')
    inlines = [CategoryBookingInline]

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    readonly_fields = ('created_at', 'updated_at')