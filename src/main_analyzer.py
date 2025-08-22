#!/usr/bin/env python3
"""
Main Database Analyzer
Orchestrates the complete analysis pipeline for any database
"""

import os
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .extractors.schema_extractor import MultiDBSchemaExtractor
from .analyzers.gemini_analyzer import GeminiSchemaAnalyzer, GeminiConfig
from .analyzers.pattern_analyzer import PatternAnalyzer
from .visualizers.graph_generator import DatabaseGraphGenerator
from .visualizers.consolidated_report_generator import ConsolidatedReportGenerator

class DatabaseAnalyzer:
    """Main orchestrator for database analysis"""
    
    def __init__(self, output_dir: str = "analysis_results", gemini_config: Optional[GeminiConfig] = None):
        self.output_dir = output_dir
        self.databases = {}
        self.extractor = MultiDBSchemaExtractor()
        
        # Initialize Gemini configuration
        if gemini_config is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            gemini_config = GeminiConfig(api_key=api_key)
        
        self.gemini_analyzer = GeminiSchemaAnalyzer(gemini_config)
        self.pattern_analyzer = PatternAnalyzer(gemini_config)
        self.graph_generator = DatabaseGraphGenerator(output_dir=f"{output_dir}_graphs")
        self.consolidated_generator = ConsolidatedReportGenerator(output_dir="consolidated_analysis")
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = f"{self.output_dir}/analysis.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def add_database(self, name: str, connection_string: str, db_type: str = "sqlite", description: str = ""):
        """Add a database for analysis"""
        self.databases[name] = {
            'connection_string': connection_string,
            'db_type': db_type,
            'description': description
        }
        self.logger.info(f"Added database: {name} ({db_type})")
    
    def analyze_all_databases(self) -> Dict[str, Any]:
        """Analyze all added databases"""
        self.logger.info("Starting multi-database analysis")
        results = {}
        
        for db_name, db_config in self.databases.items():
            try:
                self.logger.info(f"Analyzing database: {db_name}")
                
                # Extract schema
                schema_data = self.extractor.extract_relational_schema(
                    db_config['connection_string']
                )
                
                if not schema_data:
                    self.logger.error(f"Failed to extract schema for {db_name}")
                    results[db_name] = {'status': 'error', 'message': 'Schema extraction failed'}
                    continue
                
                # Analyze with Gemini
                self.logger.info("Starting Gemini schema analysis")
                analysis = self.gemini_analyzer.analyze_schema(schema_data)
                
                if not analysis:
                    self.logger.error(f"Failed to analyze {db_name} with Gemini")
                    results[db_name] = {'status': 'error', 'message': 'Gemini analysis failed'}
                    continue
                
                # Store results
                results[db_name] = {
                    'status': 'success',
                    'schema_data': schema_data,
                    'analysis': analysis,
                    'config': db_config
                }
                
                self.logger.info(f"Successfully analyzed: {db_name}")
                
            except Exception as e:
                self.logger.error(f"Error analyzing {db_name}: {e}")
                results[db_name] = {'status': 'error', 'message': str(e)}
        
        # Run cross-database pattern analysis if multiple databases
        successful_analyses = {k: v for k, v in results.items() if v.get('status') == 'success'}
        if len(successful_analyses) > 1:
            self.logger.info("Running cross-database pattern analysis")
            try:
                pattern_analysis = self.pattern_analyzer.analyze_common_patterns(results)
                results['cross_database_patterns'] = {
                    'status': 'success',
                    'analysis': pattern_analysis
                }
            except Exception as e:
                self.logger.error(f"Pattern analysis failed: {e}")
                results['cross_database_patterns'] = {'status': 'error', 'message': str(e)}
        
        self.logger.info(f"Analysis complete - {len(successful_analyses)} databases analyzed")
        return results
    
    def export_results(self, results: Dict[str, Any]):
        """Export analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export individual database results
        for db_name, result in results.items():
            if result.get('status') == 'success' and db_name != 'cross_database_patterns':
                self._export_database_result(db_name, result, timestamp)
        
        # Export cross-database patterns
        if 'cross_database_patterns' in results:
            self._export_cross_database_result(results['cross_database_patterns'], timestamp)
        
        # Generate comprehensive report
        self.generate_comprehensive_report(results, timestamp)
        
        # Generate graphs for each database
        self._generate_all_graphs(results, timestamp)
        
        # Generate consolidated reports
        self._generate_consolidated_reports(results, timestamp)
    
    def _export_database_result(self, db_name: str, result: Dict[str, Any], timestamp: str):
        """Export individual database analysis result"""
        filename = f"{self.output_dir}/{db_name}_analysis_{timestamp}.json"
        
        # Clean up the result for export (remove large schema data)
        export_data = {
            'database_name': db_name,
            'timestamp': timestamp,
            'config': result['config'],
            'analysis': result['analysis']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported {db_name} analysis to {filename}")
    
    def _export_cross_database_result(self, result: Dict[str, Any], timestamp: str):
        """Export cross-database pattern analysis result"""
        filename = f"{self.output_dir}/cross_database_patterns_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported cross-database patterns to {filename}")
    
    def generate_comprehensive_report(self, results: Dict[str, Any], timestamp: str):
        """Generate comprehensive Markdown report"""
        filename = f"{self.output_dir}/reverse_engineering_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self._generate_report_content(results, timestamp))
        
        self.logger.info(f"Comprehensive report generated: {filename}")
    
    def _generate_report_content(self, results: Dict[str, Any], timestamp: str) -> str:
        """Generate the content for the comprehensive report"""
        successful_analyses = {k: v for k, v in results.items() if v.get('status') == 'success'}
        
        content = f"""# Database Reverse Engineering Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Type:** Multi-Database Pattern Analysis

## Executive Summary

This comprehensive reverse engineering analysis examines multiple database implementations to extract deep insights about data models, business logic, and integration opportunities.

## Database Overview

**Total Databases Analyzed:** {len(successful_analyses)}
**Analysis Success Rate:** {(len(successful_analyses) / len(results) * 100):.1f}%

"""
        
        # Individual database analysis
        for db_name, result in successful_analyses.items():
            if db_name == 'cross_database_patterns':
                continue
                
            analysis = result['analysis']
            reverse_eng = analysis.get('reverse_engineering_analysis', {})
            
            content += f"""### {db_name.replace('_', ' ').title()}

#### Business Domain
- **Primary Domain:** {reverse_eng.get('business_domain_identification', {}).get('primary_domain', 'Unknown')}
- **Confidence:** {reverse_eng.get('business_domain_identification', {}).get('confidence_score', 0)}%
- **Sub-domains:** {', '.join(reverse_eng.get('business_domain_identification', {}).get('sub_domains', []))}

#### Data Model Architecture
- **Design Pattern:** {reverse_eng.get('data_model_architecture', {}).get('design_pattern', 'Unknown')}
- **Normalization Level:** {reverse_eng.get('data_model_architecture', {}).get('normalization_level', 'Unknown')}
- **Architectural Style:** {reverse_eng.get('data_model_architecture', {}).get('architectural_style', 'Unknown')}
- **Flexibility Score:** {reverse_eng.get('data_model_architecture', {}).get('flexibility_score', 0)}/100

#### Core Entities
"""
            
            entities = reverse_eng.get('entity_relationship_mapping', {}).get('core_entities', [])
            for entity in entities[:5]:  # Show first 5
                content += f"""- **{entity.get('entity_name', 'Unknown')}** ({entity.get('table_name', 'Unknown')})
  - Purpose: {entity.get('business_purpose', 'Unknown')}
"""
            
            content += f"""
#### Data Quality Assessment
- **Referential Integrity:** {analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('referential_integrity', 'Unknown')}
- **Data Consistency:** {analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('data_consistency', 'Unknown')}
- **Completeness Score:** {analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('completeness_score', 0)}/100

#### Performance Analysis
**Identified Bottlenecks:**
"""
            
            bottlenecks = analysis.get('performance_analysis', {}).get('bottleneck_identification', [])
            for bottleneck in bottlenecks[:3]:
                content += f"- {bottleneck}\n"
            
            content += f"""
#### Primary Use Cases
"""
            
            use_cases = analysis.get('use_case_analysis', {}).get('primary_use_cases', [])
            for use_case in use_cases[:3]:
                content += f"""- **{use_case.get('use_case', 'Unknown')}**
  - {use_case.get('description', 'No description')}
  - Business Value: {use_case.get('business_value', 'Unknown')}
"""
            
            content += "\n"
        
        # Cross-database patterns
        if 'cross_database_patterns' in successful_analyses:
            content += """## Cross-Database Pattern Analysis

### Common Architectural Patterns
"""
            
            patterns = successful_analyses['cross_database_patterns']['analysis']
            reverse_eng = patterns.get('reverse_engineering_insights', {})
            
            # Add cross-database insights
            domain_analysis = reverse_eng.get('domain_analysis', {})
            if domain_analysis:
                content += f"- **Domain Patterns:** {domain_analysis.get('common_patterns', [])}\n"
            
            arch_comparison = reverse_eng.get('architectural_pattern_comparison', {})
            if arch_comparison:
                content += f"- **Architecture Comparison:** {arch_comparison.get('key_differences', [])}\n"
        
        content += f"""
## Recommendations

### Immediate Actions
1. **Data Quality Improvement:** Address identified data quality issues
2. **Performance Optimization:** Implement missing indexes and query optimizations
3. **Security Enhancement:** Implement proper PII handling and access controls

### Medium-term Improvements
1. **Architecture Modernization:** Consider microservices architecture
2. **Integration Strategy:** Implement unified data model and API layer
3. **Scalability Planning:** Design for horizontal scaling

### Long-term Considerations
1. **Event-driven Architecture:** Implement real-time data processing
2. **Advanced Analytics:** Build comprehensive data warehouse
3. **AI/ML Integration:** Leverage data for predictive analytics

## Conclusion

This reverse engineering analysis provides comprehensive insights into the data models, business logic, and integration opportunities across multiple database platforms. The findings can guide:
- Platform migration strategies
- Integration architecture design
- Performance optimization efforts
- Data governance implementation
- Scalability planning

The analysis demonstrates the value of automated schema analysis in understanding complex data ecosystems and accelerating engineering efforts.
"""
        
        return content
    
    def _generate_all_graphs(self, results: Dict[str, Any], timestamp: str):
        """Generate graphs for all analyzed databases"""
        successful_analyses = {k: v for k, v in results.items() if v.get('status') == 'success'}
        
        for db_name, result in successful_analyses.items():
            if db_name == 'cross_database_patterns':
                continue
            
            try:
                # Get database path from connection string
                connection_string = result['config']['connection_string']
                if connection_string.startswith('sqlite:///'):
                    db_path = connection_string.replace('sqlite:///', '')
                else:
                    db_path = connection_string
                
                # Set database for graph generation
                self.graph_generator.set_database(db_path, result['analysis'])
                
                # Generate all graphs
                graph_files = self.graph_generator.generate_all_graphs(db_name)
                
                # Generate HTML report
                if graph_files:
                    html_report = self.graph_generator.generate_html_report(db_name, graph_files)
                    if html_report:
                        self.logger.info(f"Generated HTML report: {html_report}")
                
            except Exception as e:
                self.logger.error(f"Error generating graphs for {db_name}: {e}")
    
    def _generate_consolidated_reports(self, results: Dict[str, Any], timestamp: str):
        """Generate consolidated reports for each database"""
        successful_analyses = {k: v for k, v in results.items() if v.get('status') == 'success'}
        
        for db_name, result in successful_analyses.items():
            if db_name == 'cross_database_patterns':
                continue
            
            try:
                # Get database path from connection string
                connection_string = result['config']['connection_string']
                if connection_string.startswith('sqlite:///'):
                    db_path = connection_string.replace('sqlite:///', '')
                else:
                    db_path = connection_string
                
                # Get graph files
                graph_dir = f"{self.output_dir}_graphs"
                graph_files = {}
                if os.path.exists(graph_dir):
                    for file in os.listdir(graph_dir):
                        if file.startswith(f"{db_name}_") and file.endswith('.png'):
                            graph_type = file.replace(f"{db_name}_", "").replace('.png', '')
                            graph_files[graph_type] = os.path.join(graph_dir, file)
                
                # Generate consolidated report
                consolidated_file = self.consolidated_generator.generate_consolidated_report(
                    db_path, db_name, result, graph_files
                )
                
                self.logger.info(f"Generated consolidated report: {consolidated_file}")
                
            except Exception as e:
                self.logger.error(f"Error generating consolidated report for {db_name}: {e}")
    
    def cleanup_temporary_files(self, keep_consolidated: bool = True):
        """Clean up temporary analysis files, keeping only consolidated reports"""
        print("🧹 Cleaning up temporary analysis files...")
        
        try:
            # Remove individual analysis directories
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
                print(f"   ✅ Removed: {self.output_dir}")
            
            # Remove graph directories
            graph_dir = f"{self.output_dir}_graphs"
            if os.path.exists(graph_dir):
                shutil.rmtree(graph_dir)
                print(f"   ✅ Removed: {graph_dir}")
            
            # Keep consolidated analysis directory
            if keep_consolidated and os.path.exists("consolidated_analysis"):
                print(f"   📁 Kept: consolidated_analysis/ (consolidated reports)")
            
            print("✅ Cleanup completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def analyze_single_database(self, db_path: str, db_name: str = None, description: str = "") -> Dict[str, Any]:
        """Analyze a single database file directly"""
        if not db_name:
            db_name = Path(db_path).stem
        
        # Add the database
        connection_string = f"sqlite:///{db_path}"
        self.add_database(db_name, connection_string, "sqlite", description)
        
        # Run analysis
        results = self.analyze_all_databases()
        
        # Export results
        self.export_results(results)
        
        return results
