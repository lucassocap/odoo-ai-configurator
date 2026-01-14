#!/usr/bin/env python3
"""
Fix Module Installation - Automated
Installs problematic modules automatically
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import Orchestrator


def main():
    print("🔧 Instalando módulos faltantes automáticamente")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    # Modules to install (using technical names)
    modules_to_install = [
        'stock',           # Inventory
        'purchase',        # Purchase/Supply Chain
        'account',         # Accounting
        'stock_account',   # Inventory Accounting
        'purchase_stock',  # Purchase + Stock integration
    ]
    
    print(f"\n📦 Instalando {len(modules_to_install)} módulos...")
    print("   Esto puede tomar varios minutos...\n")
    
    result = orchestrator.configure("Install missing modules", {
        'modules': modules_to_install
    })
    
    # Show results
    if result['results']:
        agent_result = result['results'][0]['result']
        
        installed = agent_result.get('installed', [])
        failed = agent_result.get('failed', [])
        
        print("\n" + "=" * 70)
        print("📊 Resultados:")
        print(f"\n✅ Instalados exitosamente ({len(installed)}):")
        for mod in installed:
            print(f"   - {mod}")
        
        if failed:
            print(f"\n❌ Fallaron ({len(failed)}):")
            for mod in failed:
                print(f"   - {mod}")
        
        print("\n" + "=" * 70)
        
        if len(installed) == len(modules_to_install):
            print("✅ ¡Todos los módulos instalados exitosamente!")
        elif installed:
            print(f"⚠️  Instalados {len(installed)} de {len(modules_to_install)} módulos")
        else:
            print("❌ No se pudo instalar ningún módulo")
            print("\nRecomendación: Actualizar Odoo a versión 17+")
    
    print("\n🔗 Verificar en: http://localhost:8069")
    print("   Apps → Installed")


if __name__ == '__main__':
    main()
