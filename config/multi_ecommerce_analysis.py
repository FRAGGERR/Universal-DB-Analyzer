#!/usr/bin/env python3

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_multi_ecommerce_analysis():
    """Run comparative analysis on multiple e-commerce implementations"""
    
    print("🛒 Multi E-commerce Database Comparative Analysis")
    print("=" * 55)
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        return 1
    
    try:
        from src.main_analyzer import DatabaseAnalyzer
        
        # Initialize analyzer
        analyzer = DatabaseAnalyzer(output_dir="multi_ecommerce_analysis")
        
        # Add databases
        analyzer.add_database(
            name='shopify_implementation',
            connection_string='sqlite:///samples/shopify_style_ecommerce.db',
            db_type='sqlite',
            description='Shopify-style e-commerce implementation'
        )
        
        analyzer.add_database(
            name='magento_implementation',
            connection_string='sqlite:///samples/magento_style_ecommerce.db',
            db_type='sqlite',
            description='Magento-style e-commerce implementation'
        )
        
        analyzer.add_database(
            name='woocommerce_implementation',
            connection_string='sqlite:///samples/woocommerce_style_ecommerce.db',
            db_type='sqlite',
            description='WooCommerce-style e-commerce implementation'
        )
        
        # Run analysis
        results = analyzer.analyze_all_databases()
        
        # Export results
        analyzer.export_results(results)
        
        # Print summary
        print_real_summary(results)
        
        return 0
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def print_real_summary(results):
    """Print summary with real analysis results"""
    print("\n" + "="*60)
    print("📊 COMPARATIVE ANALYSIS SUMMARY")
    print("="*60)
    
    platform_data = {}
    common_entities = set()
    first_platform = True
    
    for db_name, db_result in results.items():
        if isinstance(db_result, dict) and db_result.get('status') == 'success':
            analysis = db_result['analysis']
            
            # Extract data
            domain_analysis = analysis.get('domain_analysis', {})
            quality_score = analysis.get('data_quality_assessment', {}).get('quality_score', 0)
            relationships = len(analysis.get('relationship_analysis', {}).get('primary_relationships', []))
            bottlenecks = len(analysis.get('performance_analysis', {}).get('bottleneck_predictions', []))
            entities = set(domain_analysis.get('key_business_entities', []))
            
            platform_data[db_name] = {
                'quality_score': quality_score,
                'relationships': relationships,
                'bottlenecks': bottlenecks,
                'entities': entities
            }
            
            # Find common entities
            if first_platform:
                common_entities = entities
                first_platform = False
            else:
                common_entities = common_entities.intersection(entities)
    
    print(f"🏪 Platforms Analyzed: {len(platform_data)}")
    print(f"🔗 Common Entities Found: {', '.join(common_entities) if common_entities else 'None detected'}")
    
    # Platform comparison table
    print(f"\n{'Platform':<25} {'Quality':<8} {'Relations':<10} {'Bottlenecks':<12}")
    print("-" * 60)
    
    for platform, data in platform_data.items():
        platform_display = platform.replace('_implementation', '').replace('_', ' ').title()
        print(f"{platform_display:<25} {data['quality_score']:<8} {data['relationships']:<10} {data['bottlenecks']:<12}")
    
    print(f"\n📁 Detailed results in: multi_ecommerce_analysis/")

if __name__ == "__main__":
    sys.exit(run_multi_ecommerce_analysis())
