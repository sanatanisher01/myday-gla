from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # User booking routes
    path('create/<slug:event_slug>/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('my-bookings/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # Manager booking routes
    path('manager/bookings/', views.manager_bookings, name='manager_bookings'),
    path('manager/bookings/<uuid:booking_id>/', views.manager_booking_detail, name='manager_booking_detail'),
    path('manager/bookings/<uuid:booking_id>/approve/', views.approve_booking, name='approve_booking'),
    path('manager/bookings/<uuid:booking_id>/reject/', views.reject_booking, name='reject_booking'),

    # Discount routes
    path('manager/discounts/', views.discount_list, name='discount_list'),
    path('manager/discounts/create/', views.create_discount, name='create_discount'),
    path('manager/discounts/<int:discount_id>/edit/', views.edit_discount, name='edit_discount'),
    path('manager/discounts/<int:discount_id>/delete/', views.delete_discount, name='delete_discount'),

    # Apply discount
    path('apply-discount/', views.apply_discount, name='apply_discount'),
]
