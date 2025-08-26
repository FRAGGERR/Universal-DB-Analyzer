#!/usr/bin/env python3
"""
Python Analysis Service for Web Application
This service can be called from Node.js to analyze uploaded database files
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import traceback

# Add the project root to Python path to access the analysis modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also add the current directory and parent directories
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print(f"Python path: {sys.path}")
print(f"Project root: {project_root}")
print(f"Current directory: {current_dir}")
print(f"Parent directory: {parent_dir}")

def analyze_uploaded_database(file_path, analysis_id, user_id):
    """
    Analyze an uploaded database file and return results
    
    Args:
        file_path (str): Path to the uploaded file
        analysis_id (str): Unique analysis ID
        user_id (str): User ID who uploaded the file
    
    Returns:
        dict: Analysis results and status
    """
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if GEMINI_API_KEY is set
        if not os.getenv('GEMINI_API_KEY'):
            return {
                'status': 'error',
                'message': 'GEMINI_API_KEY environment variable not set',
                'timestamp': datetime.now().isoformat()
            }
        
        # Create analysis output directory
        output_dir = f"analysis_results/{user_id}/{analysis_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Get file info
        file_name = os.path.basename(file_path)
        file_ext = Path(file_name).suffix.lower()
        db_name = Path(file_name).stem
        
        # Validate file type
        supported_formats = ['.db', '.sqlite', '.sqlite3', '.csv', '.xlsx', '.json']
        if file_ext not in supported_formats:
            return {
                'status': 'error',
                'message': f'Unsupported file format: {file_ext}. Supported formats: {", ".join(supported_formats)}',
                'timestamp': datetime.now().isoformat()
            }
        
        # Start analysis
        print(f"Starting analysis of {file_name} for user {user_id}")
        
        # Import and run analysis based on file type
        if file_ext in ['.db', '.sqlite', '.sqlite3']:
            # Use universal database analyzer for SQLite files
            try:
                from universal_database_analyzer import analyze_database
                print("Successfully imported universal_database_analyzer")
            except ImportError as e:
                print(f"Import error: {e}")
                # Try alternative import paths
                try:
                    sys.path.insert(0, os.path.join(project_root, 'src'))
                    from universal_database_analyzer import analyze_database
                    print("Successfully imported from src directory")
                except ImportError:
                    # Try to find the file directly
                    analyzer_path = os.path.join(project_root, 'universal_database_analyzer.py')
                    if os.path.exists(analyzer_path):
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("universal_database_analyzer", analyzer_path)
                        universal_database_analyzer = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(universal_database_analyzer)
                        analyze_database = universal_database_analyzer.analyze_database
                        print("Successfully imported using importlib")
                    else:
                        raise ImportError(f"Could not find universal_database_analyzer at {analyzer_path}")
            
            result = analyze_database(
                db_path=file_path,
                db_name=db_name,
                description=f"Web upload analysis of {db_name}",
                output_dir=output_dir,
                generate_graphs=True,
                cleanup_temp=False  # Keep files for web display
            )
            
        elif file_ext in ['.csv', '.xlsx', '.json']:
            # Use analyze_any_database for other formats
            try:
                from analyze_any_database import analyze_database
            except ImportError:
                # Try alternative import paths
                analyzer_path = os.path.join(project_root, 'analyze_any_database.py')
                if os.path.exists(analyzer_path):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("analyze_any_database", analyzer_path)
                    analyze_any_database = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(analyze_any_database)
                    analyze_database = analyze_any_database.analyze_database
                else:
                    raise ImportError(f"Could not find analyze_any_database at {analyzer_path}")
            
            result = analyze_database(
                db_path=file_path,
                db_name=db_name,
                description=f"Web upload analysis of {db_name}"
            )
            
            # For non-SQLite files, we need to handle the output differently
            if result == 0:  # Success
                result = {
                    'status': 'success',
                    'message': f'Successfully analyzed {file_name}',
                    'analysis_type': 'data_file',
                    'file_name': file_name,
                    'output_dir': output_dir
                }
        
        # Process results
        if result:
            # Generate web-friendly output
            web_results = generate_web_results(result, output_dir, file_name, analysis_id)
            
            return {
                'status': 'success',
                'message': f'Successfully analyzed {file_name}',
                'analysis_id': analysis_id,
                'file_name': file_name,
                'results': web_results,
                'output_dir': output_dir,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'error',
                'message': f'Analysis failed for {file_name}',
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        error_msg = f"Analysis error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        return {
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().isoformat()
        }

def generate_web_results(analysis_result, output_dir, file_name, analysis_id):
    """
    Generate web-friendly results from the analysis
    """
    
    try:
        # Create web results structure
        web_results = {
            'analysis_id': analysis_id,
            'file_name': file_name,
            'analysis_date': datetime.now().isoformat(),
            'summary': {},
            'files_generated': [],
            'insights': {},
            'visualizations': []
        }
        
        # Extract key insights from analysis result
        if isinstance(analysis_result, dict):
            if 'analysis' in analysis_result:
                analysis = analysis_result['analysis']
                
                # Extract business domain
                if 'reverse_engineering_analysis' in analysis:
                    reverse_eng = analysis['reverse_engineering_analysis']
                    if 'business_domain_identification' in reverse_eng:
                        domain_info = reverse_eng['business_domain_identification']
                        web_results['summary']['business_domain'] = domain_info.get('primary_domain', 'Unknown')
                        web_results['summary']['confidence_score'] = domain_info.get('confidence_score', 0)
                
                # Extract table information
                if 'metadata_extraction' in analysis:
                    metadata = analysis['metadata_extraction']
                    if 'tables' in metadata:
                        web_results['summary']['total_tables'] = len(metadata['tables'])
                        web_results['summary']['tables'] = list(metadata['tables'].keys())
                
                # Extract data quality info
                if 'data_quality_assessment' in analysis:
                    quality = analysis['data_quality_assessment']
                    web_results['insights']['data_quality'] = quality
        
        # List generated files
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, output_dir)
                    
                    if file.endswith(('.html', '.pdf', '.png', '.jpg', '.svg')):
                        web_results['files_generated'].append({
                            'name': file,
                            'path': rel_path,
                            'type': 'report' if file.endswith(('.html', '.pdf')) else 'visualization'
                        })
                    
                    if file.endswith(('.png', '.jpg', '.svg')):
                        web_results['visualizations'].append({
                            'name': file,
                            'path': rel_path,
                            'type': 'chart'
                        })
        
        return web_results
        
    except Exception as e:
        print(f"Error generating web results: {e}")
        return {
            'analysis_id': analysis_id,
            'file_name': file_name,
            'error': str(e)
        }

def get_analysis_status(analysis_id, user_id):
    """
    Get the current status of an analysis
    """
    try:
        output_dir = f"analysis_results/{user_id}/{analysis_id}"
        
        if not os.path.exists(output_dir):
            return {
                'status': 'not_found',
                'message': 'Analysis not found'
            }
        
        # Check for completion marker
        completion_file = os.path.join(output_dir, 'analysis_complete.txt')
        if os.path.exists(completion_file):
            with open(completion_file, 'r') as f:
                completion_data = json.load(f)
            return {
                'status': 'completed',
                'message': 'Analysis completed successfully',
                'data': completion_data
            }
        
        # Check for error marker
        error_file = os.path.join(output_dir, 'analysis_error.txt')
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                error_data = json.load(f)
            return {
                'status': 'error',
                'message': 'Analysis failed',
                'error': error_data
            }
        
        # Check if analysis is in progress
        if os.path.exists(output_dir):
            return {
                'status': 'in_progress',
                'message': 'Analysis in progress'
            }
        
        return {
            'status': 'unknown',
            'message': 'Analysis status unknown'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error checking status: {str(e)}'
        }

if __name__ == "__main__":
    # Test the service
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        analysis_id = sys.argv[2] if len(sys.argv) > 2 else "test_123"
        user_id = sys.argv[3] if len(sys.argv) > 3 else "test_user"
        
        result = analyze_uploaded_database(file_path, analysis_id, user_id)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python pythonAnalysisService.py <file_path> [analysis_id] [user_id]")
