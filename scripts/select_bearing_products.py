#!/usr/bin/env python3
"""
Select Bearing Products
Select 20 bearing products with photos and descriptions for website
"""
import csv
import json
import random
from pathlib import Path


def select_products(inventory_file, output_file, limit=20):
    """Select products with images and descriptions"""
    print(f"🔍 Selecting {limit} bearing products...")
    print("=" * 70)
    
    products = []
    base_dir = Path("/Users/lucasnapoli/Desktop/projects/TradingAgents-main")
    
    with open(inventory_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            sku = row.get('SKU', '').strip()
            image_path_rel = row.get('Image_Path', '').strip()
            
            # Skip if no image path
            if not image_path_rel:
                continue
            
            # Check if image exists
            image_path = base_dir / image_path_rel
            if not image_path.exists():
                continue
            
            
            # Create product name (translate SKU to readable name)
            product_name = f"{row.get('Brand', 'Generic')} Bearing {sku}"
            
            # Product qualifies!
            product = {
                "sku": sku,
                "name": product_name,
                "price": parse_price(row.get('Price', row.get('Cost', '0'))),
                "description": f"High-quality {row.get('Brand', 'industrial')} bearing. SKU: {sku}",
                "image_path": str(image_path),
                "category": categorize_bearing(sku, sku),
                "brand": row.get('Brand', 'Generic')
            }
            
            products.append(product)
            print(f"   ✅ {sku} - {product_name}")
            
            if len(products) >= limit:
                break
    
    print(f"\n✅ Selected {len(products)} products")
    
    # Save to JSON
    output_data = {
        "products": products,
        "total": len(products),
        "categories": list(set(p['category'] for p in products)),
        "brands": list(set(p['brand'] for p in products if p['brand']))
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Products: {len(products)}")
    print(f"   Categories: {len(output_data['categories'])}")
    print(f"   Brands: {len(output_data['brands'])}")
    
    return output_data


def translate_to_english(text):
    """Translate product name to English"""
    # Simple translations for common bearing terms
    translations = {
        'Rodamiento': 'Bearing',
        'Bolas': 'Ball',
        'Rodillos': 'Roller',
        'Empuje': 'Thrust',
        'Agujas': 'Needle',
        'Cónico': 'Tapered',
        'Cilíndrico': 'Cylindrical',
        'Autoalineable': 'Self-Aligning',
        'Contacto Angular': 'Angular Contact'
    }
    
    result = text
    for spanish, english in translations.items():
        result = result.replace(spanish, english)
    
    return result


def translate_description(text):
    """Translate description to English"""
    # For now, keep original and add English prefix
    # In production, use proper translation API
    return f"High-quality bearing. {text}"


def parse_price(price_str):
    """Parse price from string"""
    try:
        # Remove currency symbols and convert
        price = price_str.replace('$', '').replace(',', '').strip()
        return float(price)
    except:
        return 0.0


def categorize_bearing(sku, description):
    """Categorize bearing based on SKU/description"""
    sku_lower = sku.lower()
    desc_lower = description.lower()
    
    if any(x in sku_lower or x in desc_lower for x in ['6', '62', '63', 'ball']):
        return 'Ball Bearings'
    elif any(x in sku_lower or x in desc_lower for x in ['nu', 'nj', 'roller', 'cylindrical']):
        return 'Roller Bearings'
    elif any(x in sku_lower or x in desc_lower for x in ['thrust', 'empuje']):
        return 'Thrust Bearings'
    elif any(x in sku_lower or x in desc_lower for x in ['needle', 'agujas']):
        return 'Needle Bearings'
    else:
        return 'Special Bearings'


def extract_brand(sku):
    """Extract brand from SKU if possible"""
    # Common bearing brands
    brands = ['SKF', 'NSK', 'NTN', 'FAG', 'TIMKEN', 'KOYO', 'INA']
    
    sku_upper = sku.upper()
    for brand in brands:
        if brand in sku_upper:
            return brand
    
    return None


def main():
    inventory_file = "/Users/lucasnapoli/Desktop/projects/TradingAgents-main/inventory_with_all_images.csv"
    output_file = "/Users/lucasnapoli/Desktop/projects/TradingAgents-main/odoo-ai-configurator/data/bearing_products.json"
    
    select_products(inventory_file, output_file, limit=20)


if __name__ == '__main__':
    main()
