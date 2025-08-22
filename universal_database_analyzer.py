#!/usr/bin/env python3
"""
Universal Database Analyzer
Analyzes any .db file and generates comprehensive insights with visualizations
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def analyze_database(db_path: str, db_name: str = None, description: str = "", 
                    output_dir: str = None, generate_graphs: bool = True,
                    cleanup_temp: bool = True) -> dict:
    """Analyze any database with comprehensive insights and graphs"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return None
    
    # Auto-generate name and description if not provided
    if not db_name:
        db_name = Path(db_path).stem
    
    if not description:
        description = f"Comprehensive analysis of {db_name} database"
    
    if not output_dir:
        output_dir = f"{db_name}_analysis"
    
    print(f"🔍 {db_name.title()} Database Analysis")
    print("=" * 50)
    print(f"Database: {db_path}")
    print(f"Description: {description}")
    print(f"Output Directory: {output_dir}")
    print(f"Generate Graphs: {'Yes' if generate_graphs else 'No'}")
    print(f"Cleanup Temporary Files: {'Yes' if cleanup_temp else 'No'}")
    print()
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please create a .env file with your Gemini API key:")
        print("GEMINI_API_KEY=your_api_key_here")
        return None
    
    try:
        from src.main_analyzer import DatabaseAnalyzer
        
        # Initialize analyzer
        analyzer = DatabaseAnalyzer(output_dir=output_dir)
        
        # Add database
        analyzer.add_database(
            name=f'{db_name}_database',
            connection_string=f'sqlite:///{db_path}',
            db_type='sqlite',
            description=description
        )
        
        # Run analysis
        print("🔍 Starting comprehensive database analysis...")
        results = analyzer.analyze_all_databases()
        
        # Export results
        analyzer.export_results(results)
        
        # Print detailed summary
        print_detailed_summary(results, db_name)
        
        # Show generated files
        show_generated_files(output_dir, db_name)
        
        # Show consolidated reports
        show_consolidated_reports(db_name)
        
        # Cleanup temporary files if requested
        if cleanup_temp:
            print(f"\n🧹 Cleaning up temporary analysis files...")
            analyzer.cleanup_temporary_files(keep_consolidated=True)
            print(f"✅ Cleanup completed! Only consolidated reports remain.")
        
        return results
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_detailed_summary(results: dict, db_name: str):
    """Print comprehensive analysis summary"""
    print("\n" + "="*70)
    print(f"📊 {db_name.upper()} DATABASE ANALYSIS SUMMARY")
    print("="*70)
    
    for db_key, db_result in results.items():
        if isinstance(db_result, dict) and db_result.get('status') == 'success':
            analysis = db_result['analysis']
            
            # Extract analysis components
            reverse_eng = analysis.get('reverse_engineering_analysis', {})
            metadata = analysis.get('metadata_extraction', {})
            quality = analysis.get('data_quality_assessment', {})
            performance = analysis.get('performance_analysis', {})
            use_cases = analysis.get('use_case_analysis', {})
            migration = analysis.get('migration_insights', {})
            
            print(f"\n🎯 Database: {db_key.replace('_', ' ').title()}")
            print("-" * 60)
            
            # Business Domain Analysis
            domain_info = reverse_eng.get('business_domain_identification', {})
            if domain_info:
                print(f"🏢 Business Domain: {domain_info.get('primary_domain', 'Unknown')}")
                print(f"📈 Confidence: {domain_info.get('confidence_score', 0)}%")
                sub_domains = domain_info.get('sub_domains', [])
                if sub_domains:
                    print(f"📂 Sub-domains: {', '.join(sub_domains)}")
                
                processes = domain_info.get('business_processes', [])
                if processes:
                    print(f"⚙️  Business Processes:")
                    for process in processes[:5]:  # Show first 5
                        print(f"   • {process}")
            
            # Architecture Analysis
            arch_info = reverse_eng.get('data_model_architecture', {})
            if arch_info:
                print(f"\n🏗️ Architecture Analysis:")
                print(f"   📐 Design Pattern: {arch_info.get('design_pattern', 'Unknown')}")
                print(f"   🔧 Architectural Style: {arch_info.get('architectural_style', 'Unknown')}")
                print(f"   📊 Normalization: {arch_info.get('normalization_level', 'Unknown')}")
                print(f"   💪 Flexibility Score: {arch_info.get('flexibility_score', 0)}/100")
            
            # Core Entities
            entity_info = reverse_eng.get('entity_relationship_mapping', {})
            entities = entity_info.get('core_entities', [])
            if entities:
                print(f"\n🎪 Core Entities ({len(entities)} found):")
                for entity in entities[:7]:  # Show first 7
                    table_name = entity.get('table_name', 'Unknown')
                    entity_name = entity.get('entity_name', 'Unknown')
                    purpose = entity.get('business_purpose', 'Unknown')[:60]
                    data_volume = entity.get('data_volume', 'Unknown')
                    print(f"   • {entity_name} ({table_name})")
                    print(f"     Purpose: {purpose}...")
                    print(f"     Data Volume: {data_volume}")
            
            # Relationships
            relationships = entity_info.get('relationships', [])
            if relationships:
                print(f"\n🔗 Key Relationships ({len(relationships)} found):")
                for rel in relationships[:5]:  # Show first 5
                    parent = rel.get('parent_entity', 'Unknown')
                    child = rel.get('child_entity', 'Unknown')
                    rel_type = rel.get('relationship_type', 'Unknown')
                    meaning = rel.get('business_meaning', 'Unknown')[:50]
                    print(f"   • {parent} ↔ {child} ({rel_type})")
                    print(f"     Meaning: {meaning}...")
            
            # Data Quality Assessment
            integrity = quality.get('integrity_analysis', {})
            if integrity:
                print(f"\n📊 Data Quality Assessment:")
                print(f"   ✅ Referential Integrity: {integrity.get('referential_integrity', 'Unknown')}")
                print(f"   📈 Data Consistency: {integrity.get('data_consistency', 'Unknown')}")
                print(f"   🎯 Completeness Score: {integrity.get('completeness_score', 0)}/100")
                
                accuracy = integrity.get('accuracy_indicators', [])
                if accuracy:
                    print(f"   ✨ Accuracy Indicators: {', '.join(accuracy)}")
            
            # Performance Analysis
            query_patterns = performance.get('query_patterns', [])
            bottlenecks = performance.get('bottleneck_identification', [])
            optimizations = performance.get('optimization_opportunities', [])
            
            if query_patterns or bottlenecks or optimizations:
                print(f"\n⚡ Performance Analysis:")
                
                if query_patterns:
                    print(f"   🔍 Query Patterns:")
                    for pattern in query_patterns[:4]:
                        print(f"     • {pattern}")
                
                if bottlenecks:
                    print(f"   ⚠️  Bottlenecks:")
                    for bottleneck in bottlenecks[:4]:
                        print(f"     • {bottleneck}")
                
                if optimizations:
                    print(f"   🚀 Optimization Opportunities:")
                    for opt in optimizations[:4]:
                        print(f"     • {opt}")
            
            # Use Cases
            primary_use_cases = use_cases.get('primary_use_cases', [])
            analytics_opps = use_cases.get('analytics_opportunities', [])
            
            if primary_use_cases:
                print(f"\n🎯 Primary Use Cases:")
                for use_case in primary_use_cases[:4]:
                    uc_name = use_case.get('use_case', 'Unknown')
                    uc_desc = use_case.get('description', 'No description')[:60]
                    uc_value = use_case.get('business_value', 'Unknown')
                    print(f"   • {uc_name}")
                    print(f"     Description: {uc_desc}...")
                    print(f"     Business Value: {uc_value}")
            
            if analytics_opps:
                print(f"\n📈 Analytics Opportunities:")
                for opp in analytics_opps[:4]:
                    print(f"     • {opp}")
            
            # Migration Insights
            complexity = migration.get('complexity_assessment', '')
            effort = migration.get('migration_effort', '')
            if complexity or effort:
                print(f"\n🔄 Migration Insights:")
                if complexity:
                    print(f"   📊 Complexity: {complexity}")
                if effort:
                    print(f"   ⏱️  Effort Estimate: {effort}")
    
    print(f"\n📁 Detailed analysis results saved in: {db_name}_analysis/")
    print(f"📄 Key files:")
    print(f"   • reverse_engineering_report_*.md - Comprehensive report")
    print(f"   • *_analysis_*.json - Detailed AI insights")
    print(f"   • complete_analysis_*.json - Full analysis data")

def show_generated_files(output_dir: str, db_name: str):
    """Show what files were generated"""
    print(f"\n🎨 Generated Files for {db_name}:")
    print("-" * 40)
    
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            for file in sorted(files):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   📄 {file} ({size:,} bytes)")
                else:
                    print(f"   📁 {file}/")
        else:
            print("   No files generated")
    else:
        print("   Output directory not found")
    
    # Check for graph directory
    graph_dir = f"{output_dir}_graphs"
    if os.path.exists(graph_dir):
        print(f"\n📊 Generated Graphs in {graph_dir}/:")
        print("-" * 40)
        graph_files = os.listdir(graph_dir)
        if graph_files:
            for file in sorted(graph_files):
                if file.endswith('.png'):
                    print(f"   🖼️  {file}")
                elif file.endswith('.html'):
                    print(f"   🌐 {file}")
        else:
            print("   No graphs generated")

def show_consolidated_reports(db_name: str):
    """Show consolidated report files"""
    print(f"\n📋 Consolidated Reports for {db_name}:")
    print("-" * 40)
    
    consolidated_dir = "consolidated_analysis"
    if os.path.exists(consolidated_dir):
        files = os.listdir(consolidated_dir)
        db_files = [f for f in files if f.startswith(f"{db_name}_") and "consolidated" in f]
        
        if db_files:
            for file in sorted(db_files):
                file_path = os.path.join(consolidated_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    file_type = "Markdown" if file.endswith('.md') else "JSON" if file.endswith('.json') else "HTML"
                    print(f"   📄 {file} ({file_type}, {size:,} bytes)")
        else:
            print("   No consolidated reports found")
    else:
        print("   Consolidated analysis directory not found")

def batch_analyze_databases(db_directory: str, pattern: str = "*.db", cleanup_temp: bool = True):
    """Analyze multiple databases in a directory"""
    db_path = Path(db_directory)
    if not db_path.exists():
        print(f"❌ Directory not found: {db_directory}")
        return
    
    db_files = list(db_path.glob(pattern))
    if not db_files:
        print(f"❌ No {pattern} files found in {db_directory}")
        return
    
    print(f"🔍 Found {len(db_files)} databases to analyze:")
    for db_file in db_files:
        print(f"   • {db_file.name}")
    
    print(f"\n🚀 Starting batch analysis...")
    
    results = {}
    for i, db_file in enumerate(db_files, 1):
        print(f"\n{'='*60}")
        print(f"📊 Analyzing {i}/{len(db_files)}: {db_file.name}")
        print(f"{'='*60}")
        
        try:
            result = analyze_database(
                str(db_file),
                db_name=db_file.stem,
                description=f"Batch analysis of {db_file.name}",
                output_dir=f"{db_file.stem}_analysis",
                cleanup_temp=cleanup_temp
            )
            if result:
                results[db_file.name] = result
        except Exception as e:
            print(f"❌ Failed to analyze {db_file.name}: {e}")
    
    print(f"\n🎉 Batch analysis complete!")
    print(f"✅ Successfully analyzed: {len(results)}/{len(db_files)} databases")
    
    # Final cleanup if requested
    if cleanup_temp:
        print(f"\n🧹 Performing final cleanup of temporary files...")
        try:
            import shutil
            for db_file in db_files:
                temp_dir = f"{db_file.stem}_analysis"
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    print(f"   ✅ Removed: {temp_dir}")
                
                graph_dir = f"{temp_dir}_graphs"
                if os.path.exists(graph_dir):
                    shutil.rmtree(graph_dir)
                    print(f"   ✅ Removed: {graph_dir}")
            
            print(f"✅ Final cleanup completed! Only consolidated reports remain.")
        except Exception as e:
            print(f"❌ Error during final cleanup: {e}")
    
    return results

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description='Universal Database Analyzer - Analyze any .db file with AI-powered insights and visualizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single database
  python universal_database_analyzer.py New_DB/sakila.db
  
  # Analyze with custom name and description
  python universal_database_analyzer.py New_DB/Chinook_Sqlite.sqlite --name chinook --description "Music store database"
  
  # Analyze without generating graphs
  python universal_database_analyzer.py New_DB/superheroes.db --no-graphs
  
  # Analyze without cleanup (keep all files)
  python universal_database_analyzer.py New_DB/sakila.db --no-cleanup
  
  # Batch analyze all .db files in a directory
  python universal_database_analyzer.py --batch New_DB --pattern "*.db"
  
  # Show available databases
  python universal_database_analyzer.py --list
        """
    )
    
    parser.add_argument('database_path', nargs='?', help='Path to the database file to analyze')
    parser.add_argument('--name', help='Custom name for the database (default: filename)')
    parser.add_argument('--description', help='Description of the database')
    parser.add_argument('--output-dir', help='Custom output directory')
    parser.add_argument('--no-graphs', action='store_true', help='Skip graph generation')
    parser.add_argument('--no-cleanup', action='store_true', help='Keep temporary analysis files')
    parser.add_argument('--batch', help='Batch analyze all databases in directory')
    parser.add_argument('--pattern', default='*.db', help='File pattern for batch analysis (default: *.db)')
    parser.add_argument('--list', action='store_true', help='List available databases and exit')
    
    args = parser.parse_args()
    
    # List available databases
    if args.list:
        print("🔍 Available Databases:")
        print("=" * 30)
        
        # Check New_DB directory
        if os.path.exists('New_DB'):
            print("\n📁 New_DB/ directory:")
            for file in os.listdir('New_DB'):
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    file_path = os.path.join('New_DB', file)
                    size = os.path.getsize(file_path)
                    print(f"   • {file} ({size:,} bytes)")
        
        # Check current directory
        current_db_files = [f for f in os.listdir('.') if f.endswith(('.db', '.sqlite', '.sqlite3'))]
        if current_db_files:
            print("\n📁 Current directory:")
            for file in current_db_files:
                size = os.path.getsize(file)
                print(f"   • {file} ({size:,} bytes)")
        
        print(f"\n💡 Usage:")
        print(f"   python universal_database_analyzer.py <database_path>")
        print(f"   python universal_database_analyzer.py --batch New_DB")
        return 0
    
    # Batch analysis
    if args.batch:
        cleanup_temp = not args.no_cleanup
        return 0 if batch_analyze_databases(args.batch, args.pattern, cleanup_temp) else 1
    
    # Single database analysis
    if not args.database_path:
        print("❌ Error: Database path is required")
        print("Use --help for usage information")
        print("\n💡 Quick start:")
        print("   python universal_database_analyzer.py New_DB/sakila.db")
        print("   python universal_database_analyzer.py --list")
        return 1
    
    # Analyze single database
    cleanup_temp = not args.no_cleanup
    result = analyze_database(
        args.database_path,
        db_name=args.name,
        description=args.description,
        output_dir=args.output_dir,
        generate_graphs=not args.no_graphs,
        cleanup_temp=cleanup_temp
    )
    
    return 0 if result else 1

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, show usage examples
        print("🔍 Universal Database Analyzer")
        print("=" * 40)
        print("\n🎯 Analyze any .db file with AI-powered insights and visualizations!")
        print("\n💡 Quick Examples:")
        print("  python universal_database_analyzer.py New_DB/sakila.db")
        print("  python universal_database_analyzer.py New_DB/Chinook_Sqlite.sqlite")
        print("  python universal_database_analyzer.py --batch New_DB")
        print("  python universal_database_analyzer.py --list")
        print("\n📚 For detailed help:")
        print("  python universal_database_analyzer.py --help")
        sys.exit(0)
    
    sys.exit(main())
