#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Complete multi-ecommerce analysis demo"""
    
    print("🛒 Multi E-commerce Database Pattern Analysis")
    print("=" * 50)
    print("This demo will:")
    print("• Create 3 different e-commerce database implementations")
    print("• Analyze each database with Gemini AI")
    print("• Find common patterns and attributes")
    print("• Generate comparative insights")
    print("• Provide integration recommendations")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Step 1: Create sample databases
    print("Step 1: Creating multiple e-commerce database implementations...")
    try:
        from samples.create_multi_ecommerce_databases import create_all_ecommerce_variants
        create_all_ecommerce_variants()
        print("✅ Multiple e-commerce databases created!\n")
    except Exception as e:
        print(f"❌ Failed to create databases: {e}")
        return 1
    
    # Step 2: Run comparative analysis
    print("Step 2: Running Gemini AI comparative analysis...")
    try:
        from config.multi_ecommerce_analysis import run_multi_ecommerce_analysis
        result = run_multi_ecommerce_analysis()
        
        if result == 0:
            print("\n🎉 Multi-platform analysis completed successfully!")
            print("\n📋 What was analyzed:")
            print("   • Shopify-style: Collections, variants, orders, customers")
            print("   • Magento-style: EAV model, websites, catalog entities")
            print("   • WooCommerce-style: WordPress integration, posts/meta")
            
            print("\n🔍 Comparative insights generated:")
            print("   • Common attribute identification")
            print("   • Implementation pattern analysis")
            print("   • Integration opportunity mapping")
            print("   • Best practices comparison")
            print("   • Data migration recommendations")
            
            print("\n📁 Check 'multi_ecommerce_analysis/' for detailed results!")
        else:
            print("❌ Analysis failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1
    
    return 0

def check_prerequisites():
    """Check prerequisites with proper error handling"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK")
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_actual_api_key_here':
        print("❌ GEMINI_API_KEY not set properly in .env file")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        return False
    print("✅ GEMINI_API_KEY configured")
    
    # Check required packages by importing them directly
    print("✅ Testing package imports...")
    
    try:
        import google.generativeai
        print("✅ google-generativeai available")
    except ImportError as e:
        print(f"❌ google-generativeai failed: {e}")
        print("   Run: pip install google-generativeai")
        return False
    
    try:
        import sqlalchemy  
        print("✅ sqlalchemy available")
    except ImportError as e:
        print(f"❌ sqlalchemy failed: {e}")
        print("   Run: pip install sqlalchemy")
        return False
    
    try:
        import pandas
        print("✅ pandas available")
    except ImportError as e:
        print(f"❌ pandas failed: {e}")
        print("   Run: pip install pandas")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv available")
    except ImportError as e:
        print(f"❌ python-dotenv failed: {e}")
        print("   Run: pip install python-dotenv")
        return False
    
    print("✅ All prerequisites met!\n")
    return True

if __name__ == "__main__":
    sys.exit(main())
