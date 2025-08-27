from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product, Category, Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'product_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['product_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Media & Links', {
            'fields': ('logo', 'website'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('product_count',),
            'classes': ('collapse',)
        })
    )
    
    def product_count(self, obj):
        """Display number of products for this brand"""
        count = obj.products.count()
        if count > 0:
            url = reverse('admin:products_product_changelist') + f'?brand__id__exact={obj.id}'
            return format_html('<a href="{}">{} products</a>', url, count)
        return '0 products'
    product_count.short_description = 'Products'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'product_count', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['product_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('product_count',),
            'classes': ('collapse',)
        })
    )
    
    def product_count(self, obj):
        """Display number of products in this category"""
        count = obj.products.count()
        if count > 0:
            url = reverse('admin:products_product_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} products</a>', url, count)
        return '0 products'
    product_count.short_description = 'Products'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('products')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'brand', 'category', 'price', 'stock', 'rating', 
        'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'brand', 'category', 'created_at', 'rating'
    ]
    search_fields = ['name', 'description', 'sku', 'brand__name']
    list_editable = ['price', 'stock', 'is_active']
    readonly_fields = ['created_at', 'updated_at', 'formatted_tags']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'brand', 'category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock')
        }),
        ('Product Details', {
            'fields': ('description', 'tags', 'formatted_tags', 'rating'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Custom filters
    class StockFilter(admin.SimpleListFilter):
        title = 'stock level'
        parameter_name = 'stock_level'
        
        def lookups(self, request, model_admin):
            return (
                ('in_stock', 'In Stock'),
                ('low_stock', 'Low Stock (< 10)'),
                ('out_of_stock', 'Out of Stock'),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'in_stock':
                return queryset.filter(stock__gt=0)
            if self.value() == 'low_stock':
                return queryset.filter(stock__gt=0, stock__lt=10)
            if self.value() == 'out_of_stock':
                return queryset.filter(stock=0)
    
    class RatingFilter(admin.SimpleListFilter):
        title = 'rating level'
        parameter_name = 'rating_level'
        
        def lookups(self, request, model_admin):
            return (
                ('excellent', '4.5+ Stars'),
                ('good', '3.5-4.4 Stars'),
                ('average', '2.5-3.4 Stars'),
                ('poor', 'Below 2.5 Stars'),
                ('unrated', 'No Rating'),
            )
        
        def queryset(self, request, queryset):
            if self.value() == 'excellent':
                return queryset.filter(rating__gte=4.5)
            if self.value() == 'good':
                return queryset.filter(rating__gte=3.5, rating__lt=4.5)
            if self.value() == 'average':
                return queryset.filter(rating__gte=2.5, rating__lt=3.5)
            if self.value() == 'poor':
                return queryset.filter(rating__gt=0, rating__lt=2.5)
            if self.value() == 'unrated':
                return queryset.filter(rating=0)
    
    list_filter = [
        'is_active', 'brand', 'category', 'created_at', 
        StockFilter, RatingFilter
    ]
    
    def formatted_tags(self, obj):
        """Display tags in a readable format"""
        if obj.tags:
            tags_html = ""
            for tag in obj.tags:
                tags_html += f'<span style="background-color: #e1f5fe; padding: 2px 6px; margin: 2px; border-radius: 3px; font-size: 11px;">{tag}</span>'
            return mark_safe(tags_html)
        return "No tags"
    formatted_tags.short_description = 'Tags (Display)'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('brand', 'category')
    
    # Add custom actions
    actions = ['mark_as_active', 'mark_as_inactive', 'reset_stock']
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products marked as active.')
    mark_as_active.short_description = "Mark selected products as active"
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products marked as inactive.')
    mark_as_inactive.short_description = "Mark selected products as inactive"
    
    def reset_stock(self, request, queryset):
        updated = queryset.update(stock=0)
        self.message_user(request, f'Stock reset to 0 for {updated} products.')
    reset_stock.short_description = "Reset stock to 0 for selected products"


# # Optional: Inline admin for related models
# class ProductInline(admin.TabularInline):
#     model = Product
#     extra = 0
#     fields = ['name', 'price', 'stock', 'rating', 'is_active']
#     readonly_fields = ['name']
#     can_delete = False
    
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('brand', 'category')
