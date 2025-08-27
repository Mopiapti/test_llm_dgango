from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)  # Add index for search
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0, db_index=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    tags = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'brand']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.name}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # For subcategories
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name