from django import forms
from .models import Booking, Discount
from django.utils import timezone
import datetime

class BookingForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().strftime('%Y-%m-%d')}),
        help_text='Select the date for your event'
    )
    
    class Meta:
        model = Booking
        fields = ['guest_count', 'booking_date']
        widgets = {
            'guest_count': forms.NumberInput(attrs={'min': 1, 'max': 1000}),
        }

class DiscountForm(forms.ModelForm):
    valid_from = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now
    )
    valid_to = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now() + datetime.timedelta(days=30)
    )
    
    class Meta:
        model = Discount
        fields = ['code', 'description', 'percentage', 'is_active', 'valid_from', 'valid_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'percentage': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.01}),
        }
