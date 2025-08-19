#!/usr/bin/env python3

def test_setup():
    """Test if all required packages are working"""
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai imported successfully")
    except ImportError as e:
        print(f"❌ google-generativeai failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy imported successfully")
    except ImportError as e:
        print(f"❌ sqlalchemy failed: {e}")
        return False
    
    try:
        import pandas
        print(f"✅ pandas imported successfully (version: {pandas.__version__})")
    except ImportError as e:
        print(f"❌ pandas failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv failed: {e}")
        return False
    
    # Test environment
    try:
        import os
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_actual_api_key_here':
            print("✅ GEMINI_API_KEY found")
        else:
            print("❌ GEMINI_API_KEY not set properly in .env file")
    except:
        print("❌ Environment test failed")
    
    return True

if __name__ == "__main__":
    print("🔍 Testing Database Schema Analyzer Setup")
    print("=" * 45)
    
    if test_setup():
        print("\n🎉 Setup is ready! You can run the project.")
    else:
        print("\n❌ Some issues found - please fix them first.")
