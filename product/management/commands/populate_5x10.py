from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
import random

from categories.models import Category
from product.models import Product, Status
from accounts.models import CustomUser, SELLER, VIA_EMAIL, DONE


class Command(BaseCommand):
    help = "Create 5 categories and 10 products in each (50 products total)"

    def handle(self, *args, **options):
        self.stdout.write("Starting populate_5x10 command...")

        # Ensure at least one seller exists
        sellers = list(CustomUser.objects.filter(user_role=SELLER))
        if not sellers:
            self.stdout.write("No sellers found, creating a default seller user...")
            seller = CustomUser.objects.create_user(
                username="auto_seller",
                email="auto_seller@example.com",
                password="password123",
                first_name="Auto",
                last_name="Seller",
                phone_number="+998900000000",
                user_role=SELLER,
                auth_type=VIA_EMAIL,
                auth_status=DONE,
            )
            sellers = [seller]

        # Create 5 categories
        categories = []
        for i in range(1, 6):
            name = f"Dummy Category {i}"
            slug = slugify(name)
            category, created = Category.objects.get_or_create(name=name, slug=slug)
            if created:
                self.stdout.write(f"  Created category: {name}")
            else:
                self.stdout.write(f"  Using existing category: {name}")
            categories.append(category)

        # Create 10 products per category
        total = 0
        for category in categories:
            for j in range(1, 11):
                title = f"{category.name} Product {j}"
                slug = slugify(f"{title}-{random.randint(1000,9999)}")
                if Product.objects.filter(slug=slug).exists():
                    continue

                seller = random.choice(sellers)
                price = Decimal(str(round(random.uniform(10.0, 500.0), 2)))
                discount_price = None
                if random.random() > 0.7:
                    discount_price = Decimal(str(round(float(price) * (1 - random.uniform(0.05, 0.25)), 2)))

                product = Product.objects.create(
                    seller=seller,
                    category=category,
                    title=title,
                    slug=slug,
                    description="Auto-generated product for testing",
                    price=price,
                    discount_price=discount_price,
                    stock=random.randint(5, 200),
                    status=Status.PUBLISHED,
                )
                total += 1

        self.stdout.write(self.style.SUCCESS(f"Done. Created {total} products in {len(categories)} categories."))
