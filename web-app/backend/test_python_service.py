#!/usr/bin/env python3
"""
Test script for the Python Analysis Service
"""

import sys
import os
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_python_service():
    """Test the Python analysis service"""
    
    print("🧪 Testing Python Analysis Service")
    print("=" * 50)
    
    try:
        # Import the service
        from services.pythonAnalysisService import analyze_uploaded_database
        
        print("✅ Successfully imported pythonAnalysisService")
        
        # Test with a sample database file
        test_db_path = os.path.join(project_root, "New_DB", "sakila.db")
        
        if os.path.exists(test_db_path):
            print(f"📁 Found test database: {test_db_path}")
            
            # Test the analysis function
            result = analyze_uploaded_database(
                file_path=test_db_path,
                analysis_id="test_123",
                user_id="test_user"
            )
            
            print("📊 Analysis Result:")
            print(json.dumps(result, indent=2))
            
            if result and result.get('status') == 'success':
                print("✅ Python service is working correctly!")
                return True
            else:
                print("❌ Python service returned an error")
                return False
                
        else:
            print(f"⚠️  Test database not found: {test_db_path}")
            print("💡 Please ensure you have a test database file available")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required Python packages are installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_python_service()
    sys.exit(0 if success else 1)
