# -*- coding: utf-8 -*-
"""
Test verisi: 5 yeni satici (her biri icin bir kullanici hesabi) ve
bu saticilara ait ~40 urun ekler. Urun gorselleri placehold.co'dan
indirilip media/ altina kaydedilir.

Calistirma (eCommercePrj/ klasorunun icinden):
    ..\\myEcommerceWorld\\Scripts\\python.exe scripts\\seed_vendors_products.py

Script tekrar calistirilabilir: var olan kullanici/satici/urunleri
tekrar eklemez (e-posta ve urun adi + satici ile kontrol eder).

Satici hesaplarinin giris bilgileri:
    E-posta : asagidaki VENDORS listesindeki "email" alanlari
    Sifre   : TEST_PASSWORD
"""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eCommercePrj.settings")
django.setup()

import requests
from django.conf import settings
from django.db import transaction
from django.utils.text import slugify
from taggit.models import Tag

from core.models import Brand, Category, Product, Vendor
from userauths.models import User

TEST_PASSWORD = "SaticiTest123!"

VENDORS = [
    {
        "email": "teknomarket@example.com",
        "username": "TeknoMarket",
        "first_name": "Tekno",
        "last_name": "Market",
        "title": "TeknoMarket",
        "description": "Telefon, bilgisayar ve televizyonda orijinal ürün, hızlı kargo.",
        "address": "Kadıköy, İstanbul",
        "contact": "+90 532 111 22 33",
        "color": "1e3a8a",
    },
    {
        "email": "fotodunyasi@example.com",
        "username": "FotoDunyasi",
        "first_name": "Foto",
        "last_name": "Dünyası",
        "title": "Foto Dünyası",
        "description": "Profesyonel ve amatör fotoğrafçılar için kamera ve ekipman.",
        "address": "Çankaya, Ankara",
        "contact": "+90 533 222 33 44",
        "color": "7c2d12",
    },
    {
        "email": "zamansaat@example.com",
        "username": "ZamanSaat",
        "first_name": "Zaman",
        "last_name": "Saat",
        "title": "Zaman Saat & Takı",
        "description": "Lüks saat, bileklik ve yüzükte yetkili satıcı.",
        "address": "Konak, İzmir",
        "contact": "+90 534 333 44 55",
        "color": "713f12",
    },
    {
        "email": "sporplus@example.com",
        "username": "SporPlus",
        "first_name": "Spor",
        "last_name": "Plus",
        "title": "SporPlus",
        "description": "Spor ekipmanları ve lisanslı futbol formaları.",
        "address": "Nilüfer, Bursa",
        "contact": "+90 535 444 55 66",
        "color": "166534",
    },
    {
        "email": "optikmoda@example.com",
        "username": "OptikModa",
        "first_name": "Optik",
        "last_name": "Moda",
        "title": "Optik Moda",
        "description": "Güneş gözlüğü ve optik çerçevede dünya markaları.",
        "address": "Muratpaşa, Antalya",
        "contact": "+90 536 555 66 77",
        "color": "581c87",
    },
]

# (satici kullanici e-postasi, urun adi, kategori, marka, fiyat (USD), one cikan mi)
PRODUCTS = [
    # TeknoMarket
    ("teknomarket@example.com", "Samsung Galaxy S24 Ultra 256 GB", "Telefonlar", "Samsung", "1547.99", True),
    ("teknomarket@example.com", "Samsung Galaxy A55 128 GB", "Telefonlar", "Samsung", "439.99", False),
    ("teknomarket@example.com", "iPhone 15 128 GB", "Telefonlar", "Apple", "1261.99", True),
    ("teknomarket@example.com", "iPhone 14 128 GB", "Telefonlar", "Apple", "999.99", False),
    ("teknomarket@example.com", "Xiaomi 14T Pro 512 GB", "Telefonlar", "Xiaomi", "785.99", False),
    ("teknomarket@example.com", "Xiaomi Redmi Note 13 256 GB", "Telefonlar", "Xiaomi", "285.99", False),
    ("teknomarket@example.com", "Lenovo IdeaPad Slim 5 14\"", "Bilgisayarlar", "Lenovo", "666.99", False),
    ("teknomarket@example.com", "Lenovo Legion 5 Pro", "Bilgisayarlar", "Lenovo", "1309.99", True),
    ("teknomarket@example.com", "HP Victus 16 Oyun Bilgisayarı", "Bilgisayarlar", "HP", "880.99", False),
    ("teknomarket@example.com", "Asus Zenbook 14 OLED", "Bilgisayarlar", "Asus", "951.99", False),
    ("teknomarket@example.com", "Asus ROG Strix G16", "Bilgisayarlar", "Asus", "1499.99", False),
    ("teknomarket@example.com", "Samsung 55\" Crystal UHD 4K TV", "TV ve Ses Sistemleri", "Samsung", "594.99", False),
    ("teknomarket@example.com", "LG 65\" QNED 4K TV", "TV ve Ses Sistemleri", "LG", "1094.99", True),
    # Foto Dunyasi
    ("fotodunyasi@example.com", "Canon EOS R6 Mark II Gövde", "Kamera ve Fotoğraf", "Canon", "2261.99", True),
    ("fotodunyasi@example.com", "Canon EOS 250D 18-55 mm Kit", "Kamera ve Fotoğraf", "Canon", "689.99", False),
    ("fotodunyasi@example.com", "Nikon Z6 II Gövde", "Kamera ve Fotoğraf", "Nikon", "1713.99", False),
    ("fotodunyasi@example.com", "Nikon D7500 18-140 mm Kit", "Kamera ve Fotoğraf", "Nikon", "1047.99", False),
    ("fotodunyasi@example.com", "Sony Alpha a7 IV Gövde", "Kamera ve Fotoğraf", "Sony", "2142.99", True),
    ("fotodunyasi@example.com", "Sony ZV-E10 Vlog Kamerası", "Kamera ve Fotoğraf", "Sony", "594.99", False),
    ("fotodunyasi@example.com", "Sony WH-1000XM5 Kulaklık", "TV ve Ses Sistemleri", "Sony", "332.99", False),
    # Zaman Saat & Taki
    ("zamansaat@example.com", "Rolex Submariner Date", "Saatler", "Rolex", "13094.99", True),
    ("zamansaat@example.com", "Rolex Datejust 36", "Saatler", "Rolex", "9285.99", False),
    ("zamansaat@example.com", "Omega Speedmaster Moonwatch", "Saatler", "Omega", "6666.99", False),
    ("zamansaat@example.com", "Tag Heuer Carrera Chronograph", "Saatler", "Tag Heuer", "4523.99", False),
    ("zamansaat@example.com", "Pandora Kalpli Zincir Bileklik", "Bileklikler", "Pandora", "70.99", False),
    ("zamansaat@example.com", "Swarovski Tennis Bileklik", "Bileklikler", "Swarovski", "154.99", True),
    ("zamansaat@example.com", "Chamilia Gümüş Charm Bileklik", "Bileklikler", "Chamilia", "82.99", False),
    ("zamansaat@example.com", "Cartier Love Yüzük", "Yüzükler", "Cartier", "2023.99", False),
    ("zamansaat@example.com", "Bvlgari B.zero1 Yüzük", "Yüzükler", "Bvlgari", "1666.99", False),
    ("zamansaat@example.com", "Tiffany & Co. Elsa Peretti Yüzük", "Yüzükler", "Tiffany & Co.", "951.99", False),
    # SporPlus
    ("sporplus@example.com", "Nike Pegasus 41 Koşu Ayakkabısı", "Spor Ekipmanları", "Nike", "113.99", True),
    ("sporplus@example.com", "Adidas Ultraboost Light", "Spor Ekipmanları", "Adidas", "149.99", False),
    ("sporplus@example.com", "Decathlon Kipsta F500 Futbol Topu", "Spor Ekipmanları", "Decathlon", "20.99", False),
    ("sporplus@example.com", "Decathlon Domyos 20 kg Dambıl Seti", "Spor Ekipmanları", "Decathlon", "47.99", False),
    ("sporplus@example.com", "Puma Future Ultimate Krampon", "Spor Ekipmanları", "Puma", "130.99", False),
    ("sporplus@example.com", "Galatasaray 24/25 İç Saha Forması", "Futbol Formaları", "Puma", "78.99", True),
    ("sporplus@example.com", "Beşiktaş 24/25 İç Saha Forması", "Futbol Formaları", "Adidas", "75.99", False),
    ("sporplus@example.com", "Türkiye Milli Takım Forması", "Futbol Formaları", "Nike", "70.99", False),
    ("sporplus@example.com", "Trabzonspor 24/25 Forması", "Futbol Formaları", "Umbro", "66.99", False),
    # Optik Moda
    ("optikmoda@example.com", "Ray-Ban Wayfarer Classic", "Gözlükler", "Ray-Ban", "154.99", True),
    ("optikmoda@example.com", "Ray-Ban Clubmaster", "Gözlükler", "Ray-Ban", "166.99", False),
    ("optikmoda@example.com", "Oakley Holbrook Polarize", "Gözlükler", "Oakley", "178.99", False),
    ("optikmoda@example.com", "Oakley Radar EV Spor Gözlüğü", "Gözlükler", "Oakley", "213.99", False),
    ("optikmoda@example.com", "Prada Linea Rossa Güneş Gözlüğü", "Gözlükler", "Prada", "309.99", False),
]


# Urun adi -> etiketler. Ayni etiketler birden fazla urunde kullanildi ki
# etiket sayfasi (/products/tag/<slug>/) benzer urunleri bir arada gostersin.
TAGS = {
    "Samsung Galaxy S24 Ultra 256 GB": ["akıllı telefon", "amiral gemisi"],
    "Samsung Galaxy A55 128 GB": ["akıllı telefon", "fiyat performans"],
    "iPhone 15 128 GB": ["akıllı telefon", "ios"],
    "iPhone 14 128 GB": ["akıllı telefon", "ios"],
    "Xiaomi 14T Pro 512 GB": ["akıllı telefon", "amiral gemisi"],
    "Xiaomi Redmi Note 13 256 GB": ["akıllı telefon", "fiyat performans"],
    "Lenovo IdeaPad Slim 5 14\"": ["laptop", "ultrabook"],
    "Lenovo Legion 5 Pro": ["laptop", "oyun"],
    "HP Victus 16 Oyun Bilgisayarı": ["laptop", "oyun"],
    "Asus Zenbook 14 OLED": ["laptop", "ultrabook"],
    "Asus ROG Strix G16": ["laptop", "oyun"],
    "Samsung 55\" Crystal UHD 4K TV": ["televizyon", "4k"],
    "LG 65\" QNED 4K TV": ["televizyon", "4k"],
    "Canon EOS R6 Mark II Gövde": ["aynasız kamera", "profesyonel"],
    "Canon EOS 250D 18-55 mm Kit": ["dslr", "başlangıç seviyesi"],
    "Nikon Z6 II Gövde": ["aynasız kamera", "profesyonel"],
    "Nikon D7500 18-140 mm Kit": ["dslr", "başlangıç seviyesi"],
    "Sony Alpha a7 IV Gövde": ["aynasız kamera", "profesyonel"],
    "Sony ZV-E10 Vlog Kamerası": ["aynasız kamera", "vlog"],
    "Sony WH-1000XM5 Kulaklık": ["kulaklık", "gürültü engelleme"],
    "Rolex Submariner Date": ["lüks saat", "dalış saati"],
    "Rolex Datejust 36": ["lüks saat", "klasik"],
    "Omega Speedmaster Moonwatch": ["lüks saat", "kronograf"],
    "Tag Heuer Carrera Chronograph": ["lüks saat", "kronograf"],
    "Pandora Kalpli Zincir Bileklik": ["bileklik", "hediye"],
    "Swarovski Tennis Bileklik": ["bileklik", "taşlı"],
    "Chamilia Gümüş Charm Bileklik": ["bileklik", "gümüş"],
    "Cartier Love Yüzük": ["yüzük", "altın"],
    "Bvlgari B.zero1 Yüzük": ["yüzük", "altın"],
    "Tiffany & Co. Elsa Peretti Yüzük": ["yüzük", "gümüş"],
    "Nike Pegasus 41 Koşu Ayakkabısı": ["koşu", "ayakkabı"],
    "Adidas Ultraboost Light": ["koşu", "ayakkabı"],
    "Decathlon Kipsta F500 Futbol Topu": ["futbol", "top"],
    "Decathlon Domyos 20 kg Dambıl Seti": ["fitness", "ağırlık"],
    "Puma Future Ultimate Krampon": ["futbol", "ayakkabı"],
    "Galatasaray 24/25 İç Saha Forması": ["forma", "galatasaray"],
    "Beşiktaş 24/25 İç Saha Forması": ["forma", "beşiktaş"],
    "Türkiye Milli Takım Forması": ["forma", "milli takım"],
    "Trabzonspor 24/25 Forması": ["forma", "trabzonspor"],
    "Ray-Ban Wayfarer Classic": ["güneş gözlüğü", "klasik"],
    "Ray-Ban Clubmaster": ["güneş gözlüğü", "klasik"],
    "Oakley Holbrook Polarize": ["güneş gözlüğü", "polarize"],
    "Oakley Radar EV Spor Gözlüğü": ["güneş gözlüğü", "spor"],
    "Prada Linea Rossa Güneş Gözlüğü": ["güneş gözlüğü", "lüks"],
}


def download_placeholder(text, folder, filename, color):
    """placehold.co'dan uzerinde yazi olan bir gorsel indirir ve media/ altina kaydeder.
    ImageField'a yazilacak, MEDIA_ROOT'a gore goreli yolu dondurur."""
    rel_path = f"{folder}/{filename}"
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    if not os.path.exists(abs_path):
        url = f"https://placehold.co/800x800/{color}/ffffff/png?text={requests.utils.quote(text)}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(abs_path, "wb") as f:
            f.write(resp.content)
        print(f"  gorsel indirildi: {rel_path}")
    return rel_path


def create_vendor(data):
    user, created = User.objects.get_or_create(
        email=data["email"],
        defaults={
            "username": data["username"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "is_vendor": True,
        },
    )
    if created:
        user.set_password(TEST_PASSWORD)
        user.save()
        print(f"Kullanici olusturuldu: {user.email}")

    vendor = Vendor.objects.filter(user=user).first()
    if vendor:
        print(f"Satici zaten var: {vendor.title}")
        return vendor

    image = download_placeholder(
        data["title"], f"user_{user.id}", f"{slugify(data['username'])}-logo.png", data["color"]
    )
    vendor = Vendor(
        user=user,
        title=data["title"],
        description=data["description"],
        address=data["address"],
        country="Türkiye",
        contact=data["contact"],
        chat_resp_time="30",
        shipping_on_time="95",
        authentic_rating="98",
        days_return="14",
        warranty_period="24",
    )
    vendor.image.name = image  # dosya zaten indirildi, sadece yolu yaziyoruz
    vendor.save()
    print(f"Satici olusturuldu: {vendor.title}")
    return vendor


TR_TO_ASCII = str.maketrans("ıİşŞğĞüÜöÖçÇ", "iIsSgGuUoOcC")


def add_tags(product):
    # taggit Turkce karakterli slug uretir (akıllı-telefon). urls.py'deki
    # <slug:...> bunu kabul etmedigi icin etiketi ASCII slug ile kendimiz olusturuyoruz.
    for name in TAGS.get(product.title, []):
        tag, _ = Tag.objects.get_or_create(
            name=name, defaults={"slug": slugify(name.translate(TR_TO_ASCII))}
        )
        product.tags.add(tag)  # ayni etiketi ikinci kez eklemez


def create_product(vendor, title, category_title, brand_title, price, featured, color):
    existing = Product.objects.filter(title=title, vendor=vendor).first()
    if existing:
        add_tags(existing)
        print(f"  urun zaten var (etiketler guncellendi): {title}")
        return

    category = Category.objects.get(title=category_title)
    brand = Brand.objects.get(title=brand_title)
    image = download_placeholder(title, "product-images", f"{slugify(title)}.png", color)

    product = Product(
        title=title,
        description=f"<p>{title}. {brand.title} güvencesiyle, {vendor.title} mağazasından.</p>",
        specifications=f"<ul><li>Marka: {brand.title}</li><li>Kategori: {category.title}</li>"
        f"<li>Garanti: {vendor.warranty_period} ay</li></ul>",
        category=category,
        brand=brand,
        vendor=vendor,
        price=price,
        featured=featured,
        product_status="published",
    )
    product.image.name = image
    product.save()
    add_tags(product)  # m2m iliski oldugu icin urun kaydedildikten sonra eklenir
    print(f"  urun eklendi: {title}")


def main():
    with transaction.atomic():
        vendors = {}
        for data in VENDORS:
            vendors[data["email"]] = (create_vendor(data), data["color"])

        for email, title, category, brand, price, featured in PRODUCTS:
            vendor, color = vendors[email]
            create_product(vendor, title, category, brand, price, featured, color)

    print(f"\nToplam satici: {Vendor.objects.count()}, toplam urun: {Product.objects.count()}")


if __name__ == "__main__":
    main()
