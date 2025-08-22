#!/usr/bin/env python3

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def analyze_database(db_path, db_name=None, description=None):
    """Analyze any SQLite database with deep insights"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return 1
    
    # Auto-generate name and description if not provided
    if not db_name:
        db_name = os.path.splitext(os.path.basename(db_path))[0]
    
    if not description:
        description = f"Analysis of {db_name} database"
    
    print(f"🔍 {db_name.title()} Database Deep Analysis")
    print("=" * 50)
    print(f"Analyzing database: {db_path}")
    print(f"Description: {description}")
    print()
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        return 1
    
    try:
        from src.main_analyzer import DatabaseAnalyzer
        
        # Initialize analyzer with custom output directory
        output_dir = f"{db_name}_analysis"
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
        
        return 0
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def print_detailed_summary(results, db_name):
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
    print(f"   • {db_name}_database_analysis_*.json - Detailed AI insights")
    print(f"   • complete_analysis_*.json - Full analysis data")

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Analyze any SQLite database with AI-powered insights')
    parser.add_argument('database_path', help='Path to the SQLite database file')
    parser.add_argument('--name', help='Name for the database (default: filename)')
    parser.add_argument('--description', help='Description of the database')
    
    args = parser.parse_args()
    
    return analyze_database(args.database_path, args.name, args.description)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, show usage examples
        print("🔍 Database Analysis Tool")
        print("=" * 30)
        print("\nUsage examples:")
        print("  python analyze_any_database.py New_DB/sakila.db")
        print("  python analyze_any_database.py New_DB/Chinook_Sqlite.sqlite --name chinook")
        print("  python analyze_any_database.py New_DB/superheroes.db --name superheroes --description 'Comic book heroes database'")
        print("\nAvailable databases:")
        
        # List available databases
        if os.path.exists('New_DB'):
            for file in os.listdir('New_DB'):
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    print(f"  • New_DB/{file}")
        
        print(f"\nCurrent e-commerce examples:")
        if os.path.exists('samples'):
            for file in os.listdir('samples'):
                if file.endswith('.db'):
                    print(f"  • samples/{file}")
        sys.exit(0)
    
    sys.exit(main())
