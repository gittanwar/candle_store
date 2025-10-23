from django.contrib import admin
from .models import Product, Category, Location
from django.utils.html import format_html


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'price', 'stock')
    search_fields = ('name', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_tag')  # <-- icon_tag must be here
    fields = ('name', 'icon')           # <-- form fields

    # This method MUST be indented inside the class
    def icon_tag(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit:contain;" />',
                obj.icon.url
            )
        return "-"
    icon_tag.short_description = 'Icon'
    

