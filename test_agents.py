#!/usr/bin/env python3
"""
Test script to verify all agents are working
"""

def test_agent_imports():
    """Test that all agents can be imported"""
    try:
        from agents import RFQAgent, OrderAgent, SupplierAgent, ContractAgent
        print("✅ All agents imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_agent_creation():
    """Test that agents can be created"""
    try:
        from agents import RFQAgent, OrderAgent, SupplierAgent, ContractAgent
        
        # Create agent instances
        rfq_agent = RFQAgent()
        order_agent = OrderAgent()
        supplier_agent = SupplierAgent()
        contract_agent = ContractAgent()
        
        print("✅ All agents created successfully")
        print(f"   - RFQ Agent: {rfq_agent}")
        print(f"   - Order Agent: {order_agent}")
        print(f"   - Supplier Agent: {supplier_agent}")
        print(f"   - Contract Agent: {contract_agent}")
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_agent_capabilities():
    """Test agent capabilities"""
    try:
        from agents import RFQAgent, OrderAgent, SupplierAgent, ContractAgent
        
        rfq_agent = RFQAgent()
        order_agent = OrderAgent()
        supplier_agent = SupplierAgent()
        contract_agent = ContractAgent()
        
        print("✅ Agent capabilities:")
        print(f"   - RFQ Agent capabilities: {len(rfq_agent.get_capabilities())}")
        print(f"   - Order Agent capabilities: {len(order_agent.get_capabilities())}")
        print(f"   - Supplier Agent capabilities: {len(supplier_agent.get_capabilities())}")
        print(f"   - Contract Agent capabilities: {len(contract_agent.get_capabilities())}")
        return True
    except Exception as e:
        print(f"❌ Capability test failed: {e}")
        return False

def test_procura_ai():
    """Test the main ProcuraAI system"""
    try:
        from agents.procura_ai import ProcuraAI
        
        # Create ProcuraAI instance
        procura_ai = ProcuraAI()
        print("✅ ProcuraAI system created")
        print(f"   - System status: {procura_ai.get_system_status()}")
        return True
    except Exception as e:
        print(f"❌ ProcuraAI test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing ProcuraAI Agent System")
    print("=" * 50)
    
    tests = [
        ("Agent Imports", test_agent_imports),
        ("Agent Creation", test_agent_creation),
        ("Agent Capabilities", test_agent_capabilities),
        ("ProcuraAI System", test_procura_ai)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your agentic system is ready!")
        print("\n🚀 Next steps:")
        print("   1. Start your Flask app: python app.py")
        print("   2. Visit http://localhost:5000/agents/chat")
        print("   3. Try: 'Show me underperforming suppliers'")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()








