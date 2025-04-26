from django.contrib import admin
from .models import Event, SubEvent, Category, EventGallery, SubEventGallery, Review

class EventGalleryInline(admin.TabularInline):
    model = EventGallery
    extra = 1

class SubEventInline(admin.TabularInline):
    model = SubEvent
    extra = 1

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1

class SubEventGalleryInline(admin.TabularInline):
    model = SubEventGallery
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'updated_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [EventGalleryInline, SubEventInline, ReviewInline]

@admin.register(SubEvent)
class SubEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'created_at')
    list_filter = ('event', 'created_at')
    search_fields = ('name', 'description')
    inlines = [CategoryInline, SubEventGalleryInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_event', 'price', 'created_at')
    list_filter = ('sub_event', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'event')
    search_fields = ('comment',)
    readonly_fields = ('created_at',)