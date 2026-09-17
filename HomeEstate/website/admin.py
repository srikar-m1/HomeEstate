from django.contrib import admin

from .models import Favorite, Inquiry, Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'listing_type', 'price', 'owner', 'is_available')
    list_filter = ('listing_type', 'property_type', 'is_available', 'city')
    search_fields = ('title', 'description', 'city', 'owner__email')


admin.site.register(Favorite)
admin.site.register(Inquiry)

# Register your models here.
