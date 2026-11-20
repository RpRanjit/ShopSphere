from django.contrib import admin
from .models import Product, Category
# Register your models here.
# admin.site.register(Product)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=(
        'name',
        'description',
        'created_at',
    )

    search_fields = ('name',)

    ordering = ('name', )



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'is_active',
        'created_at',
    )

    list_filter = ('is_active','category')

    search_fields = ('name', 'description',)

    ordering = ('name',)



