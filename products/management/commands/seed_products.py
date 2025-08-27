from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, Category, Brand
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed the database with sample products, categories, and brands'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Product.objects.all().delete()
            Category.objects.all().delete()
            Brand.objects.all().delete()
            self.stdout.write(self.style.WARNING('Existing data cleared.'))

        with transaction.atomic():
            # Create Categories
            categories_data = [
                {
                    'name': 'Electronics',
                    'slug': 'electronics',
                    'description': 'Electronic devices and gadgets including smartphones, laptops, and accessories.'
                },
                {
                    'name': 'Clothing',
                    'slug': 'clothing',
                    'description': 'Fashion and apparel for men, women, and children.'
                },
                {
                    'name': 'Home & Garden',
                    'slug': 'home-garden',
                    'description': 'Home improvement, furniture, and garden supplies.'
                }
            ]

            categories = []
            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults=cat_data
                )
                categories.append(category)
                if created:
                    self.stdout.write(f'Created category: {category.name}')

            # Create Brands
            brands_data = [
                # Electronics brands
                {'name': 'Apple', 'slug': 'apple', 'website': 'https://apple.com'},
                {'name': 'Samsung', 'slug': 'samsung', 'website': 'https://samsung.com'},
                {'name': 'Sony', 'slug': 'sony', 'website': 'https://sony.com'},
                {'name': 'Dell', 'slug': 'dell', 'website': 'https://dell.com'},
                
                # Clothing brands
                {'name': 'Nike', 'slug': 'nike', 'website': 'https://nike.com'},
                {'name': 'Adidas', 'slug': 'adidas', 'website': 'https://adidas.com'},
                {'name': 'Zara', 'slug': 'zara', 'website': 'https://zara.com'},
                {'name': 'H&M', 'slug': 'hm', 'website': 'https://hm.com'},
                
                # Home & Garden brands
                {'name': 'IKEA', 'slug': 'ikea', 'website': 'https://ikea.com'},
                {'name': 'Home Depot', 'slug': 'home-depot', 'website': 'https://homedepot.com'},
                {'name': 'Wayfair', 'slug': 'wayfair', 'website': 'https://wayfair.com'},
            ]

            brands = []
            for brand_data in brands_data:
                brand, created = Brand.objects.get_or_create(
                    slug=brand_data['slug'],
                    defaults=brand_data
                )
                brands.append(brand)
                if created:
                    self.stdout.write(f'Created brand: {brand.name}')

            # Create Products
            products_data = [
                # Electronics (10 products)
                {
                    'name': 'iPhone 15 Pro',
                    'brand': 'Apple',
                    'category': 'Electronics',
                    'price': Decimal('999.99'),
                    'stock': 50,
                    'rating': 4.7,
                    'tags': ['smartphone', 'ios', 'premium'],
                    'description': 'Latest iPhone with A17 Pro chip and titanium design.',
                    'sku': 'APL-IPH15P-001'
                },
                {
                    'name': 'MacBook Air M3',
                    'brand': 'Apple',
                    'category': 'Electronics',
                    'price': Decimal('1299.99'),
                    'stock': 25,
                    'rating': 4.8,
                    'tags': ['laptop', 'macbook', 'apple-silicon'],
                    'description': 'Ultra-thin laptop powered by M3 chip with incredible battery life.',
                    'sku': 'APL-MBA-M3-001'
                },
                {
                    'name': 'Galaxy S24 Ultra',
                    'brand': 'Samsung',
                    'category': 'Electronics',
                    'price': Decimal('1199.99'),
                    'stock': 35,
                    'rating': 4.6,
                    'tags': ['smartphone', 'android', 'premium', 's-pen'],
                    'description': 'Premium Android phone with S Pen and 200MP camera.',
                    'sku': 'SAM-GS24U-001'
                },
                {
                    'name': 'PlayStation 5',
                    'brand': 'Sony',
                    'category': 'Electronics',
                    'price': Decimal('499.99'),
                    'stock': 15,
                    'rating': 4.5,
                    'tags': ['gaming', 'console', 'playstation'],
                    'description': 'Next-generation gaming console with 4K gaming and ray tracing.',
                    'sku': 'SNY-PS5-001'
                },
                {
                    'name': 'WH-1000XM5 Headphones',
                    'brand': 'Sony',
                    'category': 'Electronics',
                    'price': Decimal('399.99'),
                    'stock': 40,
                    'rating': 4.4,
                    'tags': ['headphones', 'noise-canceling', 'wireless'],
                    'description': 'Industry-leading noise canceling wireless headphones.',
                    'sku': 'SNY-WH1000XM5-001'
                },
                {
                    'name': 'XPS 13 Laptop',
                    'brand': 'Dell',
                    'category': 'Electronics',
                    'price': Decimal('899.99'),
                    'stock': 20,
                    'rating': 4.3,
                    'tags': ['laptop', 'ultrabook', 'windows'],
                    'description': 'Compact and powerful ultrabook for professionals.',
                    'sku': 'DEL-XPS13-001'
                },
                {
                    'name': 'Galaxy Buds Pro 3',
                    'brand': 'Samsung',
                    'category': 'Electronics',
                    'price': Decimal('249.99'),
                    'stock': 60,
                    'rating': 4.2,
                    'tags': ['earbuds', 'wireless', 'noise-canceling'],
                    'description': 'Premium wireless earbuds with adaptive noise canceling.',
                    'sku': 'SAM-GBP3-001'
                },
                {
                    'name': 'iPad Air M2',
                    'brand': 'Apple',
                    'category': 'Electronics',
                    'price': Decimal('599.99'),
                    'stock': 30,
                    'rating': 4.6,
                    'tags': ['tablet', 'ipad', 'apple-silicon'],
                    'description': 'Powerful and versatile tablet for creativity and productivity.',
                    'sku': 'APL-IPA-M2-001'
                },
                {
                    'name': '65" OLED TV',
                    'brand': 'Sony',
                    'category': 'Electronics',
                    'price': Decimal('1799.99'),
                    'stock': 8,
                    'rating': 4.7,
                    'tags': ['tv', 'oled', '4k', 'smart-tv'],
                    'description': '65-inch OLED TV with stunning picture quality and smart features.',
                    'sku': 'SNY-OLED65-001'
                },
                {
                    'name': 'Alienware Gaming Laptop',
                    'brand': 'Dell',
                    'category': 'Electronics',
                    'price': Decimal('2299.99'),
                    'stock': 12,
                    'rating': 4.4,
                    'tags': ['laptop', 'gaming', 'high-performance'],
                    'description': 'High-performance gaming laptop with RTX graphics.',
                    'sku': 'DEL-ALW-001'
                },

                # Clothing (10 products)
                {
                    'name': 'Air Jordan 1 Retro High',
                    'brand': 'Nike',
                    'category': 'Clothing',
                    'price': Decimal('169.99'),
                    'stock': 45,
                    'rating': 4.5,
                    'tags': ['shoes', 'sneakers', 'jordan', 'basketball'],
                    'description': 'Classic basketball sneakers with timeless style.',
                    'sku': 'NIK-AJ1R-001'
                },
                {
                    'name': 'Ultraboost 23 Running Shoes',
                    'brand': 'Adidas',
                    'category': 'Clothing',
                    'price': Decimal('189.99'),
                    'stock': 55,
                    'rating': 4.3,
                    'tags': ['shoes', 'running', 'boost', 'athletic'],
                    'description': 'Premium running shoes with responsive Boost midsole.',
                    'sku': 'ADI-UB23-001'
                },
                {
                    'name': 'Oversized Blazer',
                    'brand': 'Zara',
                    'category': 'Clothing',
                    'price': Decimal('79.99'),
                    'stock': 25,
                    'rating': 4.1,
                    'tags': ['blazer', 'formal', 'oversized', 'women'],
                    'description': 'Trendy oversized blazer perfect for office or casual wear.',
                    'sku': 'ZAR-OBL-001'
                },
                {
                    'name': 'Conscious Cotton T-Shirt',
                    'brand': 'H&M',
                    'category': 'Clothing',
                    'price': Decimal('12.99'),
                    'stock': 100,
                    'rating': 3.9,
                    'tags': ['t-shirt', 'cotton', 'sustainable', 'basic'],
                    'description': 'Sustainable cotton t-shirt from conscious collection.',
                    'sku': 'HM-CCT-001'
                },
                {
                    'name': 'Tech Fleece Hoodie',
                    'brand': 'Nike',
                    'category': 'Clothing',
                    'price': Decimal('89.99'),
                    'stock': 35,
                    'rating': 4.4,
                    'tags': ['hoodie', 'tech-fleece', 'casual', 'warm'],
                    'description': 'Lightweight yet warm hoodie with innovative Tech Fleece.',
                    'sku': 'NIK-TFH-001'
                },
                {
                    'name': 'Stan Smith Sneakers',
                    'brand': 'Adidas',
                    'category': 'Clothing',
                    'price': Decimal('79.99'),
                    'stock': 70,
                    'rating': 4.6,
                    'tags': ['shoes', 'sneakers', 'classic', 'white'],
                    'description': 'Iconic white leather sneakers with timeless design.',
                    'sku': 'ADI-SS-001'
                },
                {
                    'name': 'Midi Wrap Dress',
                    'brand': 'Zara',
                    'category': 'Clothing',
                    'price': Decimal('49.99'),
                    'stock': 30,
                    'rating': 4.2,
                    'tags': ['dress', 'midi', 'wrap', 'women'],
                    'description': 'Elegant midi wrap dress suitable for various occasions.',
                    'sku': 'ZAR-MWD-001'
                },
                {
                    'name': 'Organic Cotton Jeans',
                    'brand': 'H&M',
                    'category': 'Clothing',
                    'price': Decimal('39.99'),
                    'stock': 65,
                    'rating': 4.0,
                    'tags': ['jeans', 'organic', 'sustainable', 'denim'],
                    'description': 'Comfortable jeans made from organic cotton.',
                    'sku': 'HM-OCJ-001'
                },
                {
                    'name': 'Dri-FIT Training Shorts',
                    'brand': 'Nike',
                    'category': 'Clothing',
                    'price': Decimal('34.99'),
                    'stock': 80,
                    'rating': 4.3,
                    'tags': ['shorts', 'training', 'dri-fit', 'athletic'],
                    'description': 'Moisture-wicking training shorts for intense workouts.',
                    'sku': 'NIK-DFT-001'
                },
                {
                    'name': 'Firebird Track Jacket',
                    'brand': 'Adidas',
                    'category': 'Clothing',
                    'price': Decimal('69.99'),
                    'stock': 40,
                    'rating': 4.5,
                    'tags': ['jacket', 'track', 'retro', 'sporty'],
                    'description': 'Classic track jacket with iconic three stripes design.',
                    'sku': 'ADI-FTJ-001'
                },

                # Home & Garden (10 products)
                {
                    'name': 'HEMNES Bed Frame',
                    'brand': 'IKEA',
                    'category': 'Home & Garden',
                    'price': Decimal('199.99'),
                    'stock': 15,
                    'rating': 4.2,
                    'tags': ['bed', 'furniture', 'bedroom', 'wood'],
                    'description': 'Solid wood bed frame with timeless design.',
                    'sku': 'IKE-HEM-BF-001'
                },
                {
                    'name': 'KLIPPAN Loveseat Sofa',
                    'brand': 'IKEA',
                    'category': 'Home & Garden',
                    'price': Decimal('249.99'),
                    'stock': 12,
                    'rating': 4.0,
                    'tags': ['sofa', 'furniture', 'living-room', 'compact'],
                    'description': 'Compact two-seat sofa perfect for small spaces.',
                    'sku': 'IKE-KLP-LS-001'
                },
                {
                    'name': 'Cordless Drill Set',
                    'brand': 'Home Depot',
                    'category': 'Home & Garden',
                    'price': Decimal('89.99'),
                    'stock': 22,
                    'rating': 4.4,
                    'tags': ['tools', 'drill', 'cordless', 'diy'],
                    'description': 'Professional cordless drill with complete bit set.',
                    'sku': 'HD-CDS-001'
                },
                {
                    'name': '6-Tier Storage Rack',
                    'brand': 'Wayfair',
                    'category': 'Home & Garden',
                    'price': Decimal('129.99'),
                    'stock': 18,
                    'rating': 4.1,
                    'tags': ['storage', 'organization', 'rack', 'metal'],
                    'description': 'Heavy-duty metal storage rack for garage or basement.',
                    'sku': 'WAY-6TSR-001'
                },
                {
                    'name': 'Garden Hose 50ft',
                    'brand': 'Home Depot',
                    'category': 'Home & Garden',
                    'price': Decimal('34.99'),
                    'stock': 45,
                    'rating': 4.2,
                    'tags': ['garden', 'hose', 'watering', 'outdoor'],
                    'description': 'Durable 50-foot garden hose with spray nozzle.',
                    'sku': 'HD-GH50-001'
                },
                {
                    'name': 'FRIHETEN Corner Sofa-Bed',
                    'brand': 'IKEA',
                    'category': 'Home & Garden',
                    'price': Decimal('449.99'),
                    'stock': 8,
                    'rating': 4.3,
                    'tags': ['sofa', 'sofa-bed', 'corner', 'storage'],
                    'description': 'Corner sofa-bed with storage for small apartments.',
                    'sku': 'IKE-FRI-CSB-001'
                },
                {
                    'name': 'Upholstered Dining Chair Set',
                    'brand': 'Wayfair',
                    'category': 'Home & Garden',
                    'price': Decimal('189.99'),
                    'stock': 20,
                    'rating': 4.0,
                    'tags': ['chairs', 'dining', 'upholstered', 'set'],
                    'description': 'Set of 2 comfortable upholstered dining chairs.',
                    'sku': 'WAY-UDC-SET-001'
                },
                {
                    'name': 'LED Work Light',
                    'brand': 'Home Depot',
                    'category': 'Home & Garden',
                    'price': Decimal('29.99'),
                    'stock': 35,
                    'rating': 4.1,
                    'tags': ['light', 'led', 'work', 'portable'],
                    'description': 'Bright LED work light for construction and repair tasks.',
                    'sku': 'HD-LWL-001'
                },
                {
                    'name': 'Bamboo Coffee Table',
                    'brand': 'Wayfair',
                    'category': 'Home & Garden',
                    'price': Decimal('159.99'),
                    'stock': 14,
                    'rating': 4.2,
                    'tags': ['table', 'coffee-table', 'bamboo', 'eco-friendly'],
                    'description': 'Sustainable bamboo coffee table with modern design.',
                    'sku': 'WAY-BCT-001'
                },
                {
                    'name': 'MALM Desk with Drawer',
                    'brand': 'IKEA',
                    'category': 'Home & Garden',
                    'price': Decimal('119.99'),
                    'stock': 25,
                    'rating': 4.3,
                    'tags': ['desk', 'office', 'drawer', 'workspace'],
                    'description': 'Simple desk with pull-out panel and drawer for storage.',
                    'sku': 'IKE-MAL-DWD-001'
                }
            ]

            # Create brand and category lookups
            brand_lookup = {brand.name: brand for brand in brands}
            category_lookup = {cat.name: cat for cat in categories}

            products_created = 0
            for product_data in products_data:
                brand = brand_lookup.get(product_data['brand'])
                category = category_lookup.get(product_data['category'])
                
                if not brand or not category:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping {product_data["name"]}: Brand or Category not found'
                        )
                    )
                    continue

                product_data_clean = {
                    'name': product_data['name'],
                    'brand': brand,
                    'category': category,
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'rating': product_data['rating'],
                    'tags': product_data['tags'],
                    'description': product_data['description'],
                    'sku': product_data['sku']
                }

                product, created = Product.objects.get_or_create(
                    sku=product_data['sku'],
                    defaults=product_data_clean
                )
                
                if created:
                    products_created += 1
                    self.stdout.write(f'Created product: {product.name}')

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSeeding completed successfully!'
                    f'\n- Categories: {len(categories)}'
                    f'\n- Brands: {len(brands)}'
                    f'\n- Products: {products_created}'
                )
            )

            # Summary by category
            self.stdout.write('\nProducts per category:')
            for category in categories:
                count = Product.objects.filter(category=category).count()
                self.stdout.write(f'  {category.name}: {count} products')