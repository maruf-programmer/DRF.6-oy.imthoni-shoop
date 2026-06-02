from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from accounts.models import CustomUser, ORDINARY_USER, SELLER, DONE, VIA_EMAIL
from categories.models import Category
from product.models import Product, Status
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write("Starting to populate dummy data...")

        # Create users
        self.create_users()

        # Create categories
        self.create_categories()

        # Create products
        self.create_products()

        self.stdout.write(self.style.SUCCESS('Successfully populated dummy data!'))

    def create_users(self):
        """Create dummy users including ordinary users and sellers"""
        self.stdout.write("Creating users...")

        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa',
            'James', 'Mary', 'William', 'Patricia', 'Richard', 'Jennifer', 'Charles',
            'Linda', 'Joseph', 'Barbara', 'Thomas', 'Susan'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'
        ]

        # Create ordinary users
        for i in range(10):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}_{last_name.lower()}{i}"
            email = f"{username}@example.com"

            if not CustomUser.objects.filter(email=email).exists():
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password='password123',
                    phone_number=f"+9989{random.randint(10000000, 99999999)}",
                    user_role=ORDINARY_USER,
                    auth_type=VIA_EMAIL,
                    auth_status=DONE
                )
                self.stdout.write(f"  Created ordinary user: {username}")

        # Create sellers
        for i in range(10):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"seller_{first_name.lower()}_{last_name.lower()}{i}"
            email = f"{username}@example.com"

            if not CustomUser.objects.filter(email=email).exists():
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password='password123',
                    phone_number=f"+9989{random.randint(10000000, 99999999)}",
                    user_role=SELLER,
                    auth_type=VIA_EMAIL,
                    auth_status=DONE
                )
                self.stdout.write(f"  Created seller: {username}")

    def create_categories(self):
        """Create 15+ product categories"""
        self.stdout.write("Creating categories...")

        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Computers & Laptops', 'slug': 'computers-laptops'},
            {'name': 'Mobile Phones', 'slug': 'mobile-phones', 'parent': 'electronics'},
            {'name': 'Tablets', 'slug': 'tablets', 'parent': 'electronics'},
            {'name': 'Clothing & Apparel', 'slug': 'clothing-apparel'},
            {'name': 'Men Clothing', 'slug': 'men-clothing', 'parent': 'clothing-apparel'},
            {'name': 'Women Clothing', 'slug': 'women-clothing', 'parent': 'clothing-apparel'},
            {'name': 'Shoes', 'slug': 'shoes', 'parent': 'clothing-apparel'},
            {'name': 'Home & Kitchen', 'slug': 'home-kitchen'},
            {'name': 'Furniture', 'slug': 'furniture', 'parent': 'home-kitchen'},
            {'name': 'Kitchen Appliances', 'slug': 'kitchen-appliances', 'parent': 'home-kitchen'},
            {'name': 'Bedding', 'slug': 'bedding', 'parent': 'home-kitchen'},
            {'name': 'Sports & Outdoors', 'slug': 'sports-outdoors'},
            {'name': 'Fitness Equipment', 'slug': 'fitness-equipment', 'parent': 'sports-outdoors'},
            {'name': 'Outdoor Gear', 'slug': 'outdoor-gear', 'parent': 'sports-outdoors'},
            {'name': 'Books & Media', 'slug': 'books-media'},
            {'name': 'Beauty & Personal Care', 'slug': 'beauty-personal-care'},
        ]

        category_map = {}
        for cat_data in categories_data:
            parent = None
            if 'parent' in cat_data:
                parent_slug = cat_data['parent']
                if parent_slug in category_map:
                    parent = category_map[parent_slug]

            if not Category.objects.filter(slug=cat_data['slug']).exists():
                category = Category.objects.create(
                    name=cat_data['name'],
                    slug=cat_data['slug'],
                    parent=parent
                )
                category_map[cat_data['slug']] = category
                self.stdout.write(f"  Created category: {cat_data['name']}")

    def create_products(self):
        """Create 100+ products with realistic data"""
        self.stdout.write("Creating products...")

        # Get all sellers and categories
        sellers = CustomUser.objects.filter(user_role=SELLER)
        categories = Category.objects.all()

        if not sellers.exists() or not categories.exists():
            self.stdout.write(self.style.WARNING("No sellers or categories found!"))
            return

        # Product templates for different categories
        products_data = [
            # Electronics - Mobile Phones
            {
                'titles': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Xiaomi 14 Ultra', 'Google Pixel 8 Pro', 'OnePlus 12', 'Motorola Edge 50', 'Nothing Phone 1', 'Oppo Find X7', 'Vivo X100', 'Realme 12 Pro+'],
                'category': 'mobile-phones',
                'price_range': (400, 1200),
                'descriptions': [
                    'High-performance smartphone with advanced camera system and 5G connectivity',
                    'Flagship mobile device with exceptional battery life and display quality',
                    'Premium smartphone featuring the latest processor and AI capabilities',
                    'Professional-grade mobile phone with excellent photography tools',
                    'Fast and reliable smartphone with smooth performance'
                ]
            },
            # Electronics - Computers
            {
                'titles': ['MacBook Pro 16"', 'Dell XPS 15', 'HP Pavilion 15', 'Lenovo ThinkBook 16', 'ASUS VivoBook 15', 'MSI GF65 Gaming', 'Acer Aspire 5', 'ROG Gaming Laptop', 'Surface Laptop Studio', 'Razer Blade 15'],
                'category': 'computers-laptops',
                'price_range': (600, 3000),
                'descriptions': [
                    'Powerful laptop ideal for professionals and content creators',
                    'Gaming laptop with dedicated graphics and high refresh rate display',
                    'Lightweight and portable notebook for everyday computing',
                    'Workstation laptop suitable for video editing and 3D rendering',
                    'Budget-friendly laptop with solid performance for general use'
                ]
            },
            # Clothing - Men
            {
                'titles': ['Casual Cotton T-Shirt', 'Oxford Button Dress Shirt', 'Wool Winter Coat', 'Denim Jeans Classic', 'Polo Shirt Premium', 'Linen Summer Shirt', 'Cardigan Sweater', 'Henley Shirt', 'Bomber Jacket', 'Sports Shorts'],
                'category': 'men-clothing',
                'price_range': (20, 150),
                'descriptions': [
                    'Comfortable and durable casual wear perfect for everyday use',
                    'Premium quality clothing item made from finest materials',
                    'Stylish apparel suitable for both casual and formal occasions',
                    'Professional clothing ideal for office and business settings',
                    'Casual summer wear perfect for warm weather season'
                ]
            },
            # Clothing - Women
            {
                'titles': ['Summer Dress Floral', 'Elegant Black Blazer', 'Skinny Jeans Blue', 'Cashmere Sweater', 'Silk Blouse White', 'Leather Jacket', 'Maxi Skirt', 'Tank Top Pack', 'Denim Shorts', 'Winter Coat'],
                'category': 'women-clothing',
                'price_range': (25, 200),
                'descriptions': [
                    'Fashionable womens apparel with contemporary design',
                    'Premium quality fabric with elegant styling',
                    'Comfortable everyday wear for all seasons',
                    'Professional clothing suitable for workplace',
                    'Trendy garment perfect for casual outings'
                ]
            },
            # Shoes
            {
                'titles': ['Running Shoes Air Max', 'Leather Dress Shoes', 'Sneakers White Classic', 'Hiking Boots Waterproof', 'Casual Loafers', 'Basketball Shoes', 'Flip Flops Comfort', 'Formal Oxford Shoes', 'Slip-on Shoes', 'Gym Training Shoes'],
                'category': 'shoes',
                'price_range': (40, 250),
                'descriptions': [
                    'Quality footwear designed for comfort and durability',
                    'Professional shoes suitable for formal occasions',
                    'Casual footwear perfect for everyday wear',
                    'Athletic shoes designed for sports performance',
                    'Comfortable shoes with ergonomic design'
                ]
            },
            # Home & Kitchen - Furniture
            {
                'titles': ['Leather Sofa 3-Seater', 'Wooden Dining Table', 'Metal Office Chair', 'Queen Bed Frame', 'Bookshelf Cabinet', 'Coffee Table Modern', 'Wall Mounted Shelf', 'Desk Lamp', 'Area Rug', 'Storage Ottoman'],
                'category': 'furniture',
                'price_range': (150, 1500),
                'descriptions': [
                    'Elegant furniture piece that adds style to any room',
                    'Durable furniture made from quality materials',
                    'Space-saving furniture perfect for small rooms',
                    'Modern furniture design with contemporary styling',
                    'Comfortable furniture ideal for relaxation'
                ]
            },
            # Kitchen Appliances
            {
                'titles': ['Stainless Steel Coffee Maker', 'Digital Air Fryer', 'Microwave Oven', 'Electric Kettle', 'Blender Smoothie Maker', 'Toaster 4 Slice', 'Food Processor', 'Rice Cooker', 'Electric Mixer', 'Juicer Fresh'],
                'category': 'kitchen-appliances',
                'price_range': (30, 300),
                'descriptions': [
                    'Modern kitchen appliance with advanced features',
                    'Compact and efficient kitchen gadget',
                    'Energy-saving appliance for everyday cooking',
                    'Professional-grade kitchen equipment',
                    'User-friendly kitchen device with multiple functions'
                ]
            },
            # Bedding
            {
                'titles': ['Egyptian Cotton Bed Sheets', 'Memory Foam Pillow', 'Comforter Set Queen', 'Mattress Protector', 'Duvet Cover Set', 'Pillow Cases Pack', 'Fleece Blanket', 'Bed Skirt', 'Throw Pillows', 'Waterproof Mattress Cover'],
                'category': 'bedding',
                'price_range': (20, 200),
                'descriptions': [
                    'Premium bedding made from soft and breathable fabric',
                    'Comfortable bedding perfect for quality sleep',
                    'Durable bedding resistant to wear and tear',
                    'Hypoallergenic bedding suitable for sensitive skin',
                    'Affordable bedding without compromising quality'
                ]
            },
            # Sports & Fitness
            {
                'titles': ['Adjustable Dumbbells Set', 'Yoga Mat Non-Slip', 'Resistance Bands Set', 'Treadmill Folding', 'Push Up Handles', 'Kettlebell 20kg', 'Gym Equipment', 'Protein Shaker', 'Jump Rope', 'Weight Bench'],
                'category': 'fitness-equipment',
                'price_range': (15, 800),
                'descriptions': [
                    'Professional fitness equipment for gym or home training',
                    'Portable exercise gear suitable for beginners and professionals',
                    'Durable sports equipment built to last',
                    'Compact fitness tool perfect for small spaces',
                    'Complete fitness equipment set for full body workout'
                ]
            },
            # Outdoor Gear
            {
                'titles': ['Camping Tent 4-Person', 'Hiking Backpack 60L', 'Sleeping Bag Winter', 'Portable BBQ Grill', 'Camping Lantern LED', 'Hiking Poles', 'Waterproof Backpack', 'Tent Floor Mat', 'Camp Chair', 'Emergency Survival Kit'],
                'category': 'outdoor-gear',
                'price_range': (30, 500),
                'descriptions': [
                    'Essential outdoor gear for camping and hiking adventures',
                    'Weather-resistant outdoor equipment',
                    'Lightweight and portable outdoor accessory',
                    'High-quality outdoor gear built for durability',
                    'Complete outdoor setup for outdoor enthusiasts'
                ]
            },
            # Beauty & Personal Care
            {
                'titles': ['Facial Cleanser', 'Moisturizer Cream', 'Anti-Aging Serum', 'Face Mask Pack', 'Hair Shampoo', 'Body Lotion', 'Sunscreen SPF 50', 'Toothbrush Electric', 'Cologne Men', 'Perfume Women'],
                'category': 'beauty-personal-care',
                'price_range': (10, 100),
                'descriptions': [
                    'Premium skincare product for glowing and healthy skin',
                    'Natural beauty product with organic ingredients',
                    'Dermatologist-approved personal care item',
                    'Long-lasting fragrance with elegant scent',
                    'Affordable beauty product with quality results'
                ]
            },
        ]

        seller_list = list(sellers)
        product_count = 0

        for product_template in products_data:
            category = Category.objects.filter(slug=product_template['category']).first()
            if not category:
                continue

            for title in product_template['titles']:
                if product_count >= 100:
                    break

                seller = random.choice(seller_list)
                price = Decimal(random.uniform(product_template['price_range'][0], product_template['price_range'][1]))
                discount_price = None
                if random.random() > 0.6:  # 40% chance of discount
                    discount_percent = random.uniform(0.1, 0.3)
                    discount_price = Decimal(float(price) * (1 - discount_percent))

                slug = slugify(title) + '-' + str(random.randint(1000, 9999))

                if not Product.objects.filter(slug=slug).exists():
                    product = Product.objects.create(
                        seller=seller,
                        category=category,
                        title=title,
                        slug=slug,
                        description=random.choice(product_template['descriptions']),
                        price=price,
                        discount_price=discount_price,
                        stock=random.randint(10, 100),
                        status=Status.PUBLISHED
                    )
                    product_count += 1
                    if product_count % 10 == 0:
                        self.stdout.write(f"  Created {product_count} products...")

        self.stdout.write(f"  Total products created: {product_count}")
