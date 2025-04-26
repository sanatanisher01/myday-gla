from django import forms
from .models import Event, SubEvent, Category, EventGallery, Review

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'cover_photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class SubEventForm(forms.ModelForm):
    class Meta:
        model = SubEvent
        fields = ['name', 'description', 'cover_image', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }

class EventGalleryForm(forms.ModelForm):
    class Meta:
        model = EventGallery
        fields = ['image', 'caption', 'category']
        widgets = {
            'caption': forms.TextInput(attrs={'placeholder': 'Optional caption for the image'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this event'}),
            'rating': forms.RadioSelect(attrs={'class': 'rating-select'}),
        }
