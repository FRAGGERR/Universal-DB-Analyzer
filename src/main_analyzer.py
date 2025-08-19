import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

from .extractors.schema_extractor import MultiDBSchemaExtractor
from .analyzers.gemini_analyzer import GeminiSchemaAnalyzer, GeminiConfig

class DatabaseAnalyzer:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.setup_logging()
        
        # Initialize components
        self.extractor = MultiDBSchemaExtractor()
        
        # Initialize Gemini analyzer
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.analyzer = GeminiSchemaAnalyzer(
            GeminiConfig(api_key=api_key)
        )
        
        self.databases = []
        os.makedirs(output_dir, exist_ok=True)
    
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(self.output_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{self.output_dir}/analysis.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def add_database(self, name: str, connection_string: str, db_type: str, description: str = ""):
        """Add database configuration"""
        self.databases.append({
            'name': name,
            'connection_string': connection_string,
            'type': db_type.lower(),
            'description': description
        })
        self.logger.info(f"Added database: {name} ({db_type})")
    
    def analyze_all_databases(self) -> Dict[str, Any]:
        """Run complete analysis pipeline"""
        self.logger.info("Starting multi-database analysis")
        
        results = {}
        successful_analyses = []
        
        for db_config in self.databases:
            self.logger.info(f"Analyzing database: {db_config['name']}")
            
            try:
                # Extract schema
                schema_data = self.extractor.extract_relational_schema(
                    db_config['connection_string']
                )
                
                # Analyze with Gemini
                analysis = self.analyzer.analyze_schema(schema_data)
                
                # Store results
                results[db_config['name']] = {
                    'config': db_config,
                    'schema_data': schema_data,
                    'analysis': analysis,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
                
                successful_analyses.append(db_config['name'])
                self.logger.info(f"Successfully analyzed: {db_config['name']}")
                
            except Exception as e:
                self.logger.error(f"Failed to analyze {db_config['name']}: {e}")
                results[db_config['name']] = {
                    'config': db_config,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Generate summary
        results['analysis_summary'] = {
            'total_databases': len(self.databases),
            'successful_analyses': len(successful_analyses),
            'success_rate': f"{(len(successful_analyses)/len(self.databases)*100):.1f}%" if self.databases else "0%",
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Analysis complete - {len(successful_analyses)} databases analyzed")
        return results
    
    def export_results(self, results: Dict[str, Any]):
        """Export all results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export individual database results
        for db_name, db_result in results.items():
            if isinstance(db_result, dict) and db_result.get('status') == 'success':
                
                # Export analysis JSON
                analysis_file = f"{self.output_dir}/{db_name}_analysis_{timestamp}.json"
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    json.dump(db_result['analysis'], f, indent=2, default=str)
        
        # Export complete results (without large schema data)
        complete_file = f"{self.output_dir}/complete_analysis_{timestamp}.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            export_data = {}
            for key, value in results.items():
                if isinstance(value, dict):
                    export_data[key] = {k: v for k, v in value.items() if k != 'schema_data'}
                else:
                    export_data[key] = value
            
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Results exported to {self.output_dir}/")
