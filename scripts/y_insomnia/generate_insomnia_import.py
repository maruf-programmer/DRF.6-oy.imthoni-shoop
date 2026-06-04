import json
import uuid

# 1. Seed ma'lumotlarini o'qiymiz
try:
    with open('seed.json', 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
except FileNotFoundError:
    print("Xato: seed.json fayli topilmadi! Avval uni generatsiya qiling.")
    exit()

# Insomnia v4 formati asosi
insomnia_data = {
    "_type": "export",
    "__export_format": 4,
    "__export_date": "2026-06-03T18:00:00.000Z",
    "__export_source": "insomnia.desktop.app:v9.0.0",
    "resources": []
}

# Workspace (Asosiy proekt papkasi)
workspace_id = f"wrk_{uuid.uuid4().hex[:12]}"
insomnia_data["resources"].append({
    "_id": workspace_id,
    "parentId": None,
    "modified": 1700000000000,
    "created": 1700000000000,
    "name": "Imtihon 77 Shop API",
    "description": "Ustoz tekshirishi uchun barcha tayyor API so'rovlar",
    "scope": "collection",
    "_type": "workspace"
})

# Environment (Baza URL uchun o'zgaruvchi: {{ base_url }})
insomnia_data["resources"].append({
    "_id": f"env_{uuid.uuid4().hex[:12]}",
    "parentId": workspace_id,
    "modified": 1700000000000,
    "created": 1700000000000,
    "name": "Base Environment",
    "data": {
        "base_url": "http://127.0.0.1:8000/api/v1"
    },
    "dataPropertyOrder": {"&": ["base_url"]},
    "color": None,
    "isPrivate": False,
    "_type": "environment"
})

# Papka yaratish funksiyasi
def create_folder(name, parent_id):
    f_id = f"fld_{uuid.uuid4().hex[:12]}"
    insomnia_data["resources"].append({
        "_id": f_id,
        "parentId": parent_id,
        "name": name,
        "_type": "folder"
    })
    return f_id

# So'rov (Request) yaratish funksiyasi
def create_request(name, folder_id, method, path, body=None, params=None):
    r_id = f"req_{uuid.uuid4().hex[:12]}"
    req_obj = {
        "_id": r_id,
        "parentId": folder_id,
        "name": name,
        "method": method,
        "url": "{{ base_url }}" + path,
        "headers": [],
        "body": {},
        "parameters": params or [],
        "_type": "request"
    }
    if body:
        req_obj["body"] = {
            "mimeType": "application/json",
            "text": json.dumps(body, indent=2)
        }
        req_obj["headers"].append({"name": "Content-Type", "value": "application/json"})
    
    insomnia_data["resources"].append(req_obj)

# --- PAPKALARNI YARATAMIZ ---
cat_folder = create_folder("1. Categories API", workspace_id)
prod_folder = create_folder("2. Products API", workspace_id)

# --- 1. CATEGORIES API SO'ROVLARI ---
create_request("Get All Categories (List)", cat_folder, "GET", "/categories/")

if seed_data.get("categories"):
    first_cat = seed_data["categories"][0]
    create_request(f"Get Single Category (Detail) -> {first_cat['slug']}", cat_folder, "GET", f"/categories/{first_cat['id']}/")
    create_request("Update Category (PUT)", cat_folder, "PUT", f"/categories/{first_cat['id']}/", {
        "name": first_cat['name'] + " Updated",
        "slug": first_cat['slug']
    })

create_request("Create Category (POST)", cat_folder, "POST", "/categories/", {
    "name": "New Test Category",
    "slug": "new-test-category"
})

# --- 2. PRODUCTS API SO'ROVLARI ---
create_request("Get All Products (List)", prod_folder, "GET", "/products/")
create_request("Filter Products by Category Slug (Query Param)", prod_folder, "GET", "/products/", params=[
    {"name": "category", "value": "mobile-phones"}
])

if seed_data.get("products"):
    first_prod = seed_data["products"][0]
    create_request(f"Get Single Product (Detail) -> {first_prod['title']}", prod_folder, "GET", f"/products/{first_prod['id']}/")
    create_request("Update Product (PUT)", prod_folder, "PUT", f"/products/{first_prod['id']}/", {
        "title": first_prod['title'] + " Pro Max",
        "slug": first_prod['slug'] + "-pro-max",
        "category_id": first_prod['category_id']
    })

if seed_data.get("categories") and seed_data.get("products"):
    create_request("Create Product (POST)", prod_folder, "POST", "/products/", {
        "title": "Xiaomi 15 Ultra",
        "slug": "xiaomi-15-ultra-2026",
        "category_id": seed_data["categories"][0]["id"]
    })

# JSON faylga yozish
with open('insomnia_collection.json', 'w', encoding='utf-8') as f:
    json.dump(insomnia_data, f, indent=2, ensure_ascii=False)

print("\n[MUVAFFAQIYATLI] 'insomnia_collection.json' fayli yaratildi!")
print("Endi buni Insomnia-ga import qiling va ustozga ko'rsating.")