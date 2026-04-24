"""
Seed script untuk mengisi database ecommerce.db dengan data dummy.

Jalankan dari direktori backend:
    python seed.py
"""

import random
from datetime import datetime, timedelta, timezone
from slugify import slugify

from app.database import engine, SessionLocal, Base
from app.user.models import User
from app.categories.models import Category
from app.products.models import Product
from app.campaign.models import Campaign, CampaignItem
from app.orders.models import Order, OrderItem  # noqa: F401 - resolve relationships
from app.payments.models import Payment  # noqa: F401 - resolve relationships
from app.shops.models import Shop  # noqa: F401 - resolve relationships
from app.user.utils import get_password_hash


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── Categories (8 data) ──
        categories_data = [
            {"name": "Elektronik", "description": "Perangkat elektronik dan gadget", "icon": "📱"},
            {"name": "Fashion Pria", "description": "Pakaian dan aksesoris pria", "icon": "👔"},
            {"name": "Fashion Wanita", "description": "Pakaian dan aksesoris wanita", "icon": "👗"},
            {"name": "Makanan & Minuman", "description": "Produk makanan dan minuman", "icon": "🍔"},
            {"name": "Kesehatan", "description": "Produk kesehatan dan kecantikan", "icon": "💊"},
            {"name": "Olahraga", "description": "Peralatan dan perlengkapan olahraga", "icon": "⚽"},
            {"name": "Rumah Tangga", "description": "Kebutuhan rumah tangga", "icon": "🏠"},
            {"name": "Buku & Alat Tulis", "description": "Buku, alat tulis, dan perlengkapan kantor", "icon": "📚"},
        ]

        categories = []
        for data in categories_data:
            cat = Category(**data)
            db.add(cat)
            categories.append(cat)
        db.flush()

        # ── Users (4 data) ──
        users_data = [
            {"username": "budi_shop", "email": "budi@example.com", "hashed_password": get_password_hash("password123")},
            {"username": "siti_store", "email": "siti@example.com", "hashed_password": get_password_hash("password123")},
            {"username": "andi_mart", "email": "andi@example.com", "hashed_password": get_password_hash("password123")},
            {"username": "dewi_collection", "email": "dewi@example.com", "hashed_password": get_password_hash("password123")},
        ]

        users = []
        for data in users_data:
            user = User(**data)
            db.add(user)
            users.append(user)
        db.flush()

        # ── Products (masing-masing user memiliki 4-10 produk) ──
        product_pool = {
            "Elektronik": [
                ("Smartphone Android 12", 2_500_000),
                ("Laptop Gaming 15 inch", 12_000_000),
                ("Earbuds Wireless", 350_000),
                ("Kabel USB-C 1m", 45_000),
                ("Power Bank 10000mAh", 250_000),
                ("Mouse Wireless", 150_000),
                ("Keyboard Mechanical", 750_000),
                ("Webcam HD 1080p", 400_000),
                ("Speaker Bluetooth", 300_000),
                ("Charger Fast Charging", 120_000),
            ],
            "Fashion Pria": [
                ("Kaos Polos Katun", 89_000),
                ("Celana Jeans Slim Fit", 250_000),
                ("Jaket Hoodie", 180_000),
                ("Sepatu Sneakers", 450_000),
                ("Topi Baseball", 75_000),
                ("Kemeja Flannel", 165_000),
                ("Dompet Kulit", 120_000),
                ("Ikat Pinggang", 95_000),
                ("Kacamata Hitam", 130_000),
                ("Jam Tangan Digital", 350_000),
            ],
            "Fashion Wanita": [
                ("Dress Casual", 220_000),
                ("Tas Selempang", 180_000),
                ("Sandal Heels", 275_000),
                ("Blouse Satin", 165_000),
                ("Rok Plisket", 145_000),
                ("Cardigan Rajut", 200_000),
                ("Syal Pashmina", 85_000),
                ("Anting Mutiara", 110_000),
                ("Gelang Emas", 500_000),
                ("Sepatu Flat", 190_000),
            ],
            "Makanan & Minuman": [
                ("Kopi Arabika 250g", 75_000),
                ("Teh Herbal Box", 35_000),
                ("Snack Keripik Tempe", 25_000),
                ("Madu Murni 500ml", 95_000),
                ("Cokelat Bar Premium", 55_000),
                ("Granola Mix 500g", 68_000),
                ("Sambal Matah Botol", 32_000),
                ("Susu Almond 1L", 48_000),
                ("Dodol Garut", 40_000),
                ("Kerupuk Udang", 28_000),
            ],
            "Kesehatan": [
                ("Masker Wajah Aloe Vera", 25_000),
                ("Vitamin C 1000mg", 65_000),
                ("Sunscreen SPF 50", 110_000),
                ("Minyak Esensial Lavender", 85_000),
                ("Sabun Mandi Herbal", 32_000),
                ("Sikat Gigi Bambu", 18_000),
                ("Hand Sanitizer 500ml", 45_000),
                ("Lip Balm Organik", 38_000),
                ("Obat Nyamuk Alami", 28_000),
                ("Plester Luka Waterproof", 22_000),
            ],
            "Olahraga": [
                ("Matras Yoga 6mm", 175_000),
                ("Dumbbell 5kg", 120_000),
                ("Bola Basket", 250_000),
                ("Raket Badminton", 350_000),
                ("Sepatu Lari", 550_000),
                ("Resistance Band Set", 95_000),
                ("Botol Minum Sport 1L", 65_000),
                ("Skipping Rope", 45_000),
                ("Sarung Tangan Gym", 80_000),
                ("Kacamata Renang", 110_000),
            ],
            "Rumah Tangga": [
                ("Panci Stainless Steel", 220_000),
                ("Set Pisau Dapur", 185_000),
                ("Dispenser Air Minum", 350_000),
                ("Lampu LED 12W", 35_000),
                ("Rak Sepatu 4 Tingkat", 150_000),
                ("Sapu dan Pengki Set", 45_000),
                ("Gorden Blackout", 280_000),
                ("Bantal Tidur Premium", 125_000),
                ("Tempat Sampah Injak", 75_000),
                ("Talenan Kayu", 55_000),
            ],
            "Buku & Alat Tulis": [
                ("Novel Best Seller", 85_000),
                ("Buku Resep Masakan", 65_000),
                ("Pensil Warna 24 Set", 55_000),
                ("Notebook A5 Hardcover", 45_000),
                ("Pulpen Gel 0.5mm", 15_000),
                ("Buku Tulis A4 100 Lembar", 22_000),
                ("Stabilo Highlighter Set", 48_000),
                ("Penggaris Besi 30cm", 12_000),
                ("Kamus Bahasa Inggris", 95_000),
                ("Buku Mewarnai Dewasa", 38_000),
            ],
        }

        cat_names = [c.name for c in categories]
        all_products = []

        for user in users:
            num_products = random.randint(4, 10)
            used_names = set()

            for _ in range(num_products):
                cat = random.choice(categories)
                pool = product_pool[cat.name]
                name, base_price = random.choice(pool)

                # Hindari duplikat slug
                while name in used_names:
                    cat = random.choice(categories)
                    pool = product_pool[cat.name]
                    name, base_price = random.choice(pool)
                used_names.add(name)

                price = base_price + random.randint(-10_000, 20_000)
                price = max(price, 10_000)

                product = Product(
                    name=name,
                    description=f"{name} berkualitas tinggi dari {user.username}",
                    price=float(price),
                    stock=random.randint(5, 100),
                    image_url=f"https://placehold.co/400x400?text={name.replace(' ', '+')}",
                    slug=slugify(f"{name}-{user.username}"),
                    is_publish=True,
                    user_id=user.id,
                    category_id=cat.id,
                )
                db.add(product)
                all_products.append(product)

        db.flush()

        # ── Campaigns (2 campaign aktif) ──
        now = datetime.now(timezone.utc)
        campaigns_data = [
            {
                "name": "Flash Sale Ramadhan",
                "start_time": now - timedelta(days=2),
                "end_time": now + timedelta(days=12),
                "is_active": True,
            },
            {
                "name": "Promo Akhir Pekan",
                "start_time": now - timedelta(hours=6),
                "end_time": now + timedelta(days=3),
                "is_active": True,
            },
        ]

        campaigns = []
        for data in campaigns_data:
            campaign = Campaign(**data)
            db.add(campaign)
            campaigns.append(campaign)
        db.flush()

        # ── Campaign Items (produk random ke campaign aktif) ──
        random.shuffle(all_products)
        used_product_ids = set()

        for index, campaign in enumerate(campaigns):
            if index == 0:
                num_items = min(15, len(all_products))
            else:
                num_items = random.randint(3, min(6, len(all_products)))
            added = 0

            for product in all_products:
                if added >= num_items:
                    break
                if product.id in used_product_ids:
                    continue

                discount = random.uniform(0.10, 0.40)
                special_price = round(product.price * (1 - discount), -3)

                item = CampaignItem(
                    campaign_id=campaign.id,
                    product_id=product.id,
                    special_price=float(special_price),
                    stock_limit=random.randint(5, 30),
                    stock_sold=0,
                )
                db.add(item)
                used_product_ids.add(product.id)
                added += 1

        db.commit()
        print("✅ Seed berhasil!")
        print(f"   - {len(categories)} categories")
        print(f"   - {len(users)} users")
        print(f"   - {len(all_products)} products")
        print(f"   - {len(campaigns)} campaigns")
        print(f"   - {len(used_product_ids)} campaign items")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed gagal: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
