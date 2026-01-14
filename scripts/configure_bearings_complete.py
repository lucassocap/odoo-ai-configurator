#!/usr/bin/env python3
"""
Configure Bearings Inc - Complete Setup
eCommerce, CRM, Invoicing, Sales, Inventory, Supply Chain
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import Orchestrator


def main():
    print("🚀 Configurando Bearings Inc en Odoo")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    # Step 1: Configure Company
    print("\n📋 Paso 1: Configurando empresa...")
    result = orchestrator.configure("Configure company", {
        'name': 'Bearings Inc',
        'email': 'info@bearingsinc.com',
        'phone': '+1-555-BEARING',
        'website': 'https://bearingsinc.com',
        'street': '123 Industrial Blvd',
        'city': 'Chicago',
        'zip': '60601',
        'country_id': 233,  # USA
        'currency_id': 2,   # USD
    })
    print(f"   ✅ {result['results'][0]['result']['status']}")
    
    # Step 2: Install Modules
    print("\n📦 Paso 2: Instalando módulos...")
    modules = [
        'website',          # Website
        'ecommerce',        # eCommerce
        'crm',              # CRM
        'sales',            # Sales
        'invoicing',        # Invoicing
        'inventory',        # Inventory
        'purchase',         # Purchase/Supply Chain
        'accounting',       # Accounting
    ]
    
    result = orchestrator.configure("Install modules", {
        'modules': modules
    })
    
    installed = result['results'][0]['result'].get('installed', [])
    print(f"   ✅ Instalados: {len(installed)} módulos")
    for mod in installed:
        print(f"      - {mod}")
    
    # Step 3: Configure Website
    print("\n🌐 Paso 3: Configurando website...")
    result = orchestrator.configure("Configure website", {
        'publish': True,
        'ecommerce': True
    })
    print(f"   ✅ {result['results'][0]['result']['status']}")
    
    print("\n" + "=" * 70)
    print("✅ Configuración de Bearings Inc completada!")
    print("\n📊 Resumen:")
    print("   - Empresa: Bearings Inc")
    print("   - Módulos: eCommerce, CRM, Sales, Invoicing, Inventory, Supply Chain")
    print("   - Website: Publicado y configurado")
    print("\n🔗 Próximos pasos:")
    print("   1. Acceder a Odoo: http://localhost:8069")
    print("   2. Verificar módulos instalados")
    print("   3. Importar productos")
    print("   4. Configurar integraciones")


if __name__ == '__main__':
    main()
