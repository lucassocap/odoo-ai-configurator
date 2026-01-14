#!/usr/bin/env python3
"""
Test Script for Odoo AI Configurator
Simple test to verify everything works
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from orchestrator import Orchestrator


def test_connection():
    """Test 1: Connection to Odoo"""
    print("=" * 60)
    print("TEST 1: Connection to Odoo")
    print("=" * 60)
    
    try:
        orchestrator = Orchestrator(
            url="http://localhost:8069",
            db="bearings",
            username="admin",
            password="admin"
        )
        print("✅ Connected to Odoo successfully!")
        return orchestrator
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nMake sure:")
        print("1. Odoo is running (docker ps)")
        print("2. Database 'bearings' exists")
        print("3. Username/password are correct")
        return None


def test_company_agent(orchestrator):
    """Test 2: Company Agent"""
    print("\n" + "=" * 60)
    print("TEST 2: Company Configuration")
    print("=" * 60)
    
    try:
        result = orchestrator.configure("Configure company", {
            'name': 'Test Company',
            'email': 'test@example.com',
            'city': 'Test City'
        })
        
        print(f"✅ Company configured!")
        print(f"   Agents executed: {result['agents_executed']}")
        return True
    except Exception as e:
        print(f"❌ Company configuration failed: {e}")
        return False


def test_module_agent(orchestrator):
    """Test 3: Module Agent"""
    print("\n" + "=" * 60)
    print("TEST 3: Module Installation")
    print("=" * 60)
    
    try:
        # Test with friendly names
        result = orchestrator.configure("Install modules", {
            'modules': ['crm', 'sales']
        })
        
        print(f"✅ Modules configured!")
        print(f"   Agents executed: {result['agents_executed']}")
        
        # Show results
        for agent_result in result['results']:
            agent_name = agent_result['agent']
            status = agent_result['result']['status']
            print(f"   {agent_name}: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Module installation failed: {e}")
        return False


def test_natural_language(orchestrator):
    """Test 4: Natural Language"""
    print("\n" + "=" * 60)
    print("TEST 4: Natural Language Configuration")
    print("=" * 60)
    
    try:
        # Test natural language understanding
        result = orchestrator.configure("Setup eCommerce store")
        
        print(f"✅ Natural language processed!")
        print(f"   Agents executed: {result['agents_executed']}")
        print(f"   Agents: {[r['agent'] for r in result['results']]}")
        
        return True
    except Exception as e:
        print(f"❌ Natural language failed: {e}")
        return False


def main():
    print("\n🤖 Odoo AI Configurator - Test Suite")
    print("=" * 60)
    
    # Test 1: Connection
    orchestrator = test_connection()
    if not orchestrator:
        print("\n❌ Cannot proceed without Odoo connection")
        return
    
    # Test 2: Company Agent
    test_company_agent(orchestrator)
    
    # Test 3: Module Agent
    test_module_agent(orchestrator)
    
    # Test 4: Natural Language
    test_natural_language(orchestrator)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check Odoo UI: http://localhost:8069")
    print("2. Verify company name changed")
    print("3. Check installed modules")


if __name__ == '__main__':
    main()
