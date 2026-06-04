import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

import django
django.setup()

from categories.models import Category
from product.models import Product

def as_dict_category(c):
    return {'id': str(c.id), 'slug': str(c.slug), 'name': c.name}


def as_dict_product(p):
    return {
        'id': str(p.id),
        'slug': str(p.slug),
        'title': p.title,
        'category_id': str(p.category.id) if p.category else None,
    }


data = {
    'categories': [as_dict_category(c) for c in Category.objects.all()],
    'products': [as_dict_product(p) for p in Product.objects.all()],
}

print(json.dumps(data, ensure_ascii=False, indent=2))
