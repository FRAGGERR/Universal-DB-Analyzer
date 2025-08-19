import google.generativeai as genai
import json
from typing import Dict, Any
import logging
from dataclasses import dataclass

@dataclass
class GeminiConfig:
    api_key: str
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.1
    max_output_tokens: int = 8192

class GeminiSchemaAnalyzer:
    def __init__(self, config: GeminiConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(
            model_name=config.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
            )
        )
    
    def analyze_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze database schema using Gemini"""
        self.logger.info("Starting Gemini schema analysis")
        
        try:
            prompt = self._build_analysis_prompt(schema_data)
            response = self.model.generate_content(prompt)
            analysis = self._parse_response(response.text)
            
            self.logger.info("Schema analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in schema analysis: {e}")
            return self._create_error_response(str(e))
    
    def _build_analysis_prompt(self, schema_data: Dict[str, Any]) -> str:
        """Build analysis prompt for Gemini"""
        
        # Simplify schema for prompt
        simplified_schema = {}
        tables = schema_data.get('tables', {})
        
        for table_name, table_data in list(tables.items())[:10]:  # Limit to 10 tables
            columns = table_data.get('columns', [])
            simplified_schema[table_name] = {
                'column_count': len(columns),
                'columns': [col.get('name') for col in columns[:10]],  # First 10 columns
                'row_count': table_data.get('row_count', 0)
            }
        
        prompt = f"""
You are an expert database architect. Analyze this e-commerce database schema:

Database Type: {schema_data.get('database_type', 'sqlite')}
Tables: {json.dumps(simplified_schema, indent=2)}

Respond with JSON in this exact format:
{{
  "domain_analysis": {{
    "business_domain": "e-commerce",
    "application_type": "web application",
    "key_business_entities": ["Customer", "Product", "Order"],
    "confidence_score": 85
  }},
  "relationship_analysis": {{
    "primary_relationships": [
      {{"parent_table": "customers", "child_table": "orders", "relationship_type": "one-to-many"}}
    ]
  }},
  "data_quality_assessment": {{
    "normalization_level": "3NF",
    "quality_score": 80,
    "integrity_issues": []
  }},
  "performance_analysis": {{
    "bottleneck_predictions": ["Large order table scans"],
    "missing_indexes": ["orders.customer_id"],
    "query_patterns": ["Customer order history", "Product catalog browsing"]
  }},
  "recommendations": {{
    "immediate_improvements": ["Add indexes on foreign keys"],
    "long_term_refactoring": ["Consider order partitioning"]
  }}
}}

Only respond with valid JSON, nothing else.
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response"""
        try:
            response_text = response_text.strip()
            
            # Find JSON boundaries
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx + 1]
                return json.loads(json_text)
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return self._create_fallback_analysis(response_text)
    
    def _create_fallback_analysis(self, response_text: str) -> Dict[str, Any]:
        """Create fallback analysis when JSON parsing fails"""
        return {
            "domain_analysis": {
                "business_domain": "e-commerce",
                "application_type": "database system",
                "key_business_entities": ["Customer", "Product", "Order"],
                "confidence_score": 75
            },
            "relationship_analysis": {
                "primary_relationships": []
            },
            "data_quality_assessment": {
                "normalization_level": "3NF",
                "quality_score": 75,
                "integrity_issues": []
            },
            "performance_analysis": {
                "bottleneck_predictions": ["Database query performance"],
                "missing_indexes": [],
                "query_patterns": ["CRUD operations"]
            },
            "recommendations": {
                "immediate_improvements": ["Optimize database queries"],
                "long_term_refactoring": ["Consider performance tuning"]
            },
            "fallback_note": "Used fallback analysis due to parsing error"
        }
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response structure"""
        return {
            "error": error_msg,
            "domain_analysis": {"business_domain": "e-commerce", "confidence_score": 50},
            "relationship_analysis": {"primary_relationships": []},
            "data_quality_assessment": {"quality_score": 50},
            "recommendations": {"immediate_improvements": []}
        }
