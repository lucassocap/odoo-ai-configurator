#!/usr/bin/env python3
"""
Memory System Demo
Demonstrates Lessons Learned and RAG memory
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.memory import LessonsLearned, RAGMemory


def demo_lessons_learned():
    """Demonstrate Lessons Learned system"""
    print("🧠 Lessons Learned Demo")
    print("=" * 60)
    
    lessons = LessonsLearned()
    
    # Record some errors
    print("\n📝 Recording errors...")
    lessons.record_error(
        agent_name="ModuleAgent",
        error_type="IndexError",
        error_msg="tuple index out of range",
        context="Installing stock module on Odoo 16"
    )
    
    lessons.record_error(
        agent_name="ModuleAgent",
        error_type="IndexError",
        error_msg="tuple index out of range",
        context="Installing purchase module on Odoo 16"
    )
    
    # Record solution
    print("✅ Recording solution...")
    lessons.record_solution(
        agent_name="ModuleAgent",
        error_type="IndexError",
        solution="Update to Odoo 17 to fix module installation issues",
        context="Odoo 16 has compatibility issues with module search"
    )
    
    # Check if error seen before
    print("\n🔍 Checking if error seen before...")
    has_seen = lessons.has_seen_error("ModuleAgent", "IndexError")
    print(f"   Has seen IndexError: {has_seen}")
    
    # Get solutions
    print("\n💡 Getting known solutions...")
    solutions = lessons.get_solutions("ModuleAgent", "IndexError")
    for i, sol in enumerate(solutions, 1):
        print(f"   {i}. {sol['solution']}")
        print(f"      Context: {sol['context']}")
    
    # Get stats
    print("\n📊 Statistics:")
    stats = lessons.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    lessons.close()


def demo_rag_memory():
    """Demonstrate RAG memory system"""
    print("\n\n🔮 RAG Memory Demo")
    print("=" * 60)
    
    rag = RAGMemory()
    
    if not rag.enabled:
        print("⚠️  RAG not available (ChromaDB not installed)")
        print("   Install with: pip install chromadb sentence-transformers")
        return
    
    # Store some context
    print("\n📝 Storing context...")
    rag.store(
        action="configure_company",
        params={"name": "Bearings Inc", "email": "info@bearingsinc.com"},
        result="success",
        context="Configured Bearings Inc with full company details",
        agent_name="CompanyAgent"
    )
    
    rag.store(
        action="install_modules",
        params={"modules": ["website", "crm"]},
        result="success",
        context="Installed website and CRM modules for eCommerce setup",
        agent_name="ModuleAgent"
    )
    
    # Search context
    print("\n🔍 Searching for 'Bearings Inc'...")
    results = rag.search("Bearings Inc company configuration")
    for i, result in enumerate(results, 1):
        print(f"\n   Result {i}:")
        print(f"   {result['document'][:200]}...")
        print(f"   Metadata: {result['metadata']}")
    
    # Get stats
    print("\n📊 Statistics:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def main():
    print("🚀 Memory System Demo")
    print("=" * 60)
    
    demo_lessons_learned()
    demo_rag_memory()
    
    print("\n" + "=" * 60)
    print("✅ Demo complete!")


if __name__ == '__main__':
    main()
