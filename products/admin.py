from django.contrib import admin

from .models import File, Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "parent", "is_enable", "created_time"]
    list_filter = ["is_enable", "parent"]
    search_fields = ["title"]

class FileInlineAdmin(admin.TabularInline):
    model = File
    fields = ["title", "file_type", "file", "is_enable"]
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "get_categories", "is_enable", "created_time"]
    list_filter = ["is_enable"]
    search_fields = ["title", "categories"]
    inlines = [FileInlineAdmin]

    def get_categories(self, obj):
        return ", ".join([category.title for category in Category.objects.all()])
    
    get_categories.short_description = "Categories"