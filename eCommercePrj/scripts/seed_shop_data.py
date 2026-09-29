# -*- coding: utf-8 -*-
"""
Toplu veri ekleme scripti: yeni satici (Trendo), 12 yeni urun ve urun
yorumlari/degerlendirmeleri (ProductReview) ekler.

Calistirma (eCommercePrj/ klasorunun icinden, sanal ortam python'u ile):
    ..\myEcommerceWorld\Scripts\python.exe scripts\seed_shop_data.py

Script idempotent'tir: title/sku gibi benzersiz alanlara gore var olan
kayitlari tekrar eklemez, tekrar calistirmak guvenlidir.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eCommercePrj.settings")
django.setup()

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from userauths.models import User
from core.models import Category, Brand, Vendor, Product, ProductReview

MEDIA_ROOT = settings.MEDIA_ROOT


def download_placeholder(text, folder, filename):
    """placehold.co'dan urun adi yazili bir gorsel indirir, media/ altina kaydeder.
    Donen deger, ImageField'a yazilacak MEDIA_ROOT'a gore relatif yoldur."""
    rel_dir = folder
    abs_dir = os.path.join(MEDIA_ROOT, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    rel_path = f"{rel_dir}/{filename}"
    abs_path = os.path.join(MEDIA_ROOT, rel_path)
    if os.path.exists(abs_path):
        return rel_path
    url = f"https://placehold.co/800x800/e8edf2/1e293b/png?text={requests.utils.quote(text)}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    with open(abs_path, "wb") as f:
        f.write(resp.content)
    print(f"  indirildi: {rel_path}")
    return rel_path


def get_or_create_merodoe():
    user, created = User.objects.get_or_create(
        email="merodoe@example.com",
        defaults={
            "username": "MeroDoe",
            "first_name": "Mero",
            "last_name": "Doe",
            "phone": "05550000000",
            "is_active": True,
            "is_staff": False,
        },
    )
    if created:
        user.set_password("merodoe123")
        user.save()
        print("Kullanici olusturuldu: MeroDoe (merodoe@example.com / merodoe123)")
    else:
        print("Kullanici zaten var: MeroDoe")
    return user


def get_or_create_trendo(owner):
    vendor = Vendor.objects.filter(title="Trendo").first()
    if vendor:
        print("Satici zaten var: Trendo")
        return vendor
    image_path = download_placeholder("Trendo", "user_directory_trendo", "trendo_logo.png")
    vendor = Vendor.objects.create(
        title="Trendo",
        image=image_path,
        description="Teknolojiden aksesuara genis urun yelpazesiyle Trendo.",
        address="Levent, Istanbul",
        country="Turkiye",
        contact="+90 212 555 04 04",
        chat_resp_time="92",
        shipping_on_time="95",
        authentic_rating="98",
        days_return="30",
        warranty_period="24",
        user=owner,
    )
    print(f"Satici olusturuldu: Trendo (user={owner.username})")
    return vendor


PRODUCTS = [
    # (title, category_id, brand_title, price, old_price, stock, vendor_key, description, specifications, featured)
    # category_id: 1 Telefonlar, 2 Bilgisayarlar, 3 TV ve Ses Sistemleri, 4 Kamera ve Fotograf,
    # 5 Saatler, 6 Bileklikler, 7 Spor Ekipmanlari, 8 Yuzukler, 9 Gozlukler
    ("iPhone 15 Pro Max", 1, "Apple", "64999.99", "69999.99", "15", "trendo",
     "Apple iPhone 15 Pro Max, 256GB, Dogal Titanyum. A17 Pro cip ile ustun performans.",
     "Ekran: 6.7 inc Super Retina XDR, Islemci: A17 Pro, RAM: 8GB, Depolama: 256GB", True),
    ("Lenovo ThinkPad X1 Carbon", 2, "Lenovo", "42999.99", "47999.99", "10", "trendo",
     "Lenovo ThinkPad X1 Carbon Gen 11. Is dunyasi icin tasarlanmis ultra hafif laptop.",
     "Ekran: 14 inc 2.8K OLED, Islemci: Intel Core i7-1365U, RAM: 16GB, SSD: 512GB", True),
    ("Sony Bravia 55\" 4K TV", 3, "Sony", "34999.99", "39999.99", "8", "trendo",
     "Sony Bravia 55 inc 4K HDR Google TV. Sinema kalitesinde goruntu deneyimi.",
     "Ekran: 55 inc 4K LED, HDR: Dolby Vision, Ses: Dolby Atmos, Isletim Sistemi: Google TV", False),
    ("Canon EOS R50", 4, "Canon", "27999.99", "31999.99", "6", "trendo",
     "Canon EOS R50 aynasiz fotograf makinesi. Baslangic seviyesi icin ideal.",
     "Sensor: 24.2MP APS-C CMOS, ISO: 100-32000, Video: 4K 30fps, AF: Dual Pixel CMOS AF II", False),
    ("Nike Air Zoom Pegasus 40", 7, "Nike", "4499.99", "4999.99", "35", "trendo",
     "Nike Air Zoom Pegasus 40 Kosu Ayakkabisi. Gunluk antrenmanlar icin guvenilir performans.",
     "Taban: React kopuk + Zoom Air, Ust: Mesh, Agirlik: 255g", True),
    ("Ray-Ban Aviator Classic", 9, "Ray-Ban", "6999.99", "7999.99", "20", "trendo",
     "Ray-Ban Aviator Classic RB3025, Altin Cerceve / Yesil Cam. Ikonik pilot gozluk.",
     "Cerceve: Metal, Cam: Kristal Yesil G-15, UV Koruma: %100", False),

    ("Xiaomi Redmi Note 13 Pro", 1, "Xiaomi", "13999.99", "15999.99", "30", "her_telden",
     "Xiaomi Redmi Note 13 Pro, 256GB. Uygun fiyata yuksek performans.",
     "Ekran: 6.67 inc AMOLED 120Hz, Islemci: Snapdragon 7s Gen 2, RAM: 8GB, Depolama: 256GB", False),
    ("HP Pavilion 15 Gaming", 2, "HP", "22999.99", "26999.99", "12", "her_telden",
     "HP Pavilion Gaming 15, RTX 3050, i5-12500H. Oyun ve uretkenlik icin ideal.",
     "Ekran: 15.6 inc FHD 144Hz, Islemci: Intel i5-12500H, GPU: RTX 3050, RAM: 16GB, SSD: 512GB", False),
    ("LG OLED evo C4 48\"", 3, "LG", "44999.99", "54999.99", "5", "her_telden",
     "LG OLED evo C4 48 inc. Mukemmel siyah seviyeleri ve canli renkler.",
     "Ekran: 48 inc OLED evo, HDR: Dolby Vision IQ, Islemci: a9 Gen7 AI", True),
    ("Omega Seamaster Diver 300M", 5, "Omega", "289999.99", "319999.99", "3", "her_telden",
     "Omega Seamaster Diver 300M. Deniz altinda ve sehirde stil sahibi.",
     "Kasa: 42mm Paslanmaz Celik, Su Gecirmezlik: 300m, Hareket: Co-Axial Master Chronometer", True),
    ("Pandora Moments Yilan Zincir Bileklik", 6, "Pandora", "3499.99", "3999.99", "40", "her_telden",
     "Pandora Moments Yilan Zincir Bileklik, Gumus. Kendi stilinizi yaratin.",
     "Malzeme: 925 Ayar Gumus, Kilit: Varil Kilit, Uyumlu: Pandora Charms", False),
    ("Tiffany T1 Yuzuk", 8, "Tiffany & Co.", "74999.99", "84999.99", "4", "her_telden",
     "Tiffany T1 Yuzuk, 18 Ayar Altin. Modern ve cesur bir tasarim.",
     "Malzeme: 18 Ayar Sari Altin, Genislik: 4.5mm", False),
]

REVIEWS_BY_TITLE = {
    "iPhone 15 Pro Max": [
        (3, 5, "Performans inanilmaz, kamera geceleri bile cok basarili."),
        (4, 4, "Guzel telefon ama fiyati biraz yuksek geldi."),
    ],
    "Lenovo ThinkPad X1 Carbon": [
        (3, 5, "Is icin aldim, hem hafif hem cok dayanikli."),
        (4, 5, "Klavyesi ve ekrani harika, tavsiye ederim."),
    ],
    "Sony Bravia 55\" 4K TV": [
        (4, 4, "Goruntu kalitesi cok iyi, ses sistemi biraz zayif."),
    ],
    "Canon EOS R50": [
        (3, 4, "Baslangic seviyesi icin gayet yeterli bir makine."),
        (4, 5, "Otofokus hizi beklentimin ustundeydi."),
    ],
    "Nike Air Zoom Pegasus 40": [
        (3, 5, "Kosu icin aldim, ayagi hic yormuyor."),
        (4, 4, "Rahat ama biraz dar kaliyor, yarim numara buyuk alin."),
    ],
    "Ray-Ban Aviator Classic": [
        (4, 5, "Klasik tasarim hic eskimiyor, kalitesi cok iyi."),
    ],
    "Xiaomi Redmi Note 13 Pro": [
        (3, 4, "Fiyat performans olarak gayet basarili bir telefon."),
        (4, 3, "Ekran guzel ama batarya omru beklentimin altinda kaldi."),
    ],
    "HP Pavilion 15 Gaming": [
        (3, 4, "Orta seviye oyunlari rahat kaldiriyor."),
        (4, 4, "Fani biraz sesli ama performanstan memnunum."),
    ],
    "LG OLED evo C4 48\"": [
        (3, 5, "Siyah seviyeleri gercekten mukemmel, film izlemek keyif oldu."),
        (4, 5, "Fiyati yuksek ama goruntu kalitesi her seye deger."),
    ],
    "Omega Seamaster Diver 300M": [
        (3, 5, "Iscilik muhtesem, uzun sure dusunup aldim, pisman degilim."),
    ],
    "Pandora Moments Yilan Zincir Bileklik": [
        (3, 5, "Hediye olarak aldim, cok begenildi."),
        (4, 4, "Kalitesi guzel, charm'lar kolayca takiliyor."),
    ],
    "Tiffany T1 Yuzuk": [
        (4, 5, "Zarif ve sade, her kombine cok yakisiyor."),
    ],
    # Var olan urunlere de birer ek yorum
    "Samsung A23": [
        (4, 4, "Gunluk kullanim icin gayet yeterli, kamerasi iyi."),
    ],
    "Rolex Saat": [
        (3, 5, "Yillardir hayalini kurdugum saatti, kalitesi tartisilmaz."),
    ],
}


def run():
    print("=== Kullanici ve satici ===")
    merodoe = get_or_create_merodoe()
    trendo = get_or_create_trendo(merodoe)
    her_telden = Vendor.objects.get(title="Her Telden")
    merickaya = her_telden.user
    johndoe = User.objects.get(username="JohnDoe")

    vendors = {"trendo": (trendo, merodoe), "her_telden": (her_telden, merickaya)}

    print("\n=== Urunler ===")
    created_count = 0
    for (title, category_id, brand_title, price, old_price, stock, vendor_key,
         description, specifications, featured) in PRODUCTS:
        if Product.objects.filter(title=title).exists():
            print(f"  atlandi (zaten var): {title}")
            continue

        category = Category.objects.get(id=category_id)
        brand = Brand.objects.get(title=brand_title, category=category)
        vendor, owner = vendors[vendor_key]

        filename = f"{slugify(title)}.png"
        image_path = download_placeholder(title, "product-images", filename)

        Product.objects.create(
            title=title,
            image=image_path,
            description=description,
            user=owner,
            category=category,
            brand=brand,
            vendor=vendor,
            price=price,
            old_price=old_price,
            specifications=specifications,
            stock_count=stock,
            product_status="published",
            status=True,
            in_stock=True,
            featured=featured,
            digital=False,
        )
        created_count += 1
        print(f"  eklendi: {title} ({vendor.title})")
    print(f"Toplam yeni urun: {created_count}")

    print("\n=== Yorumlar / Degerlendirmeler ===")
    reviewers = {3: merickaya, 4: johndoe}
    review_created = 0
    for title, reviews in REVIEWS_BY_TITLE.items():
        try:
            product = Product.objects.get(title=title)
        except Product.DoesNotExist:
            print(f"  urun bulunamadi, atlandi: {title}")
            continue
        for user_id, rating, text in reviews:
            user = reviewers[user_id]
            if ProductReview.objects.filter(product=product, user=user).exists():
                continue
            ProductReview.objects.create(
                user=user, product=product, review=text, rating=rating,
            )
            review_created += 1
            print(f"  eklendi: {title} - {user.username} - {rating}*")
    print(f"Toplam yeni yorum: {review_created}")


if __name__ == "__main__":
    run()
