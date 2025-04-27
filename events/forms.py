from django import forms
from .models import Event, SubEvent, Category, EventGallery, Review

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'cover_photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_cover_photo(self):
        cover_photo = self.cleaned_data.get('cover_photo')
        if cover_photo:
            # Check file size (10MB limit)
            if cover_photo.size > 10 * 1024 * 1024:  # 10MB in bytes
                raise forms.ValidationError("Image file size must be under 10MB.")
        return cover_photo

class SubEventForm(forms.ModelForm):
    class Meta:
        model = SubEvent
        fields = ['name', 'description', 'cover_image', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            # Check file size (10MB limit)
            if cover_image.size > 10 * 1024 * 1024:  # 10MB in bytes
                raise forms.ValidationError("Image file size must be under 10MB.")
        return cover_image

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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (10MB limit)
            if image.size > 10 * 1024 * 1024:  # 10MB in bytes
                raise forms.ValidationError("Image file size must be under 10MB.")
        return image

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this event'}),
            'rating': forms.RadioSelect(attrs={'class': 'rating-select'}),
        }
