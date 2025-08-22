import google.generativeai as genai
import json
from typing import Dict, Any
import logging
from dataclasses import dataclass

@dataclass
class GeminiConfig:
    api_key: str
    model_name: str = "gemini-1.5-flash"  # Changed from gemini-1.5-pro to gemini-1.5-flash
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
        """Build comprehensive analysis prompt for reverse engineering"""
        
        # Extract detailed schema information
        detailed_schema = {}
        tables = schema_data.get('tables', {})
        
        for table_name, table_data in list(tables.items())[:15]:  # Increased limit
            columns = table_data.get('columns', [])
            foreign_keys = table_data.get('foreign_keys', [])
            indexes = table_data.get('indexes', [])
            primary_keys = table_data.get('primary_keys', {})
            
            detailed_schema[table_name] = {
                'column_count': len(columns),
                'columns': [
                    {
                        'name': col.get('name'),
                        'type': str(col.get('type')),
                        'nullable': col.get('nullable', True),
                        'default': col.get('default'),
                        'comment': col.get('comment', '')
                    } for col in columns
                ],
                'row_count': table_data.get('row_count', 0),
                'foreign_keys': foreign_keys,
                'indexes': indexes,
                'primary_keys': primary_keys.get('constrained_columns', [])
            }
        
        prompt = f"""
You are an expert database reverse engineer and data architect. Perform a DEEP ANALYSIS of this database schema for reverse engineering purposes.

Database Type: {schema_data.get('database_type', 'sqlite')}
Total Tables: {len(tables)}
Detailed Schema: {json.dumps(detailed_schema, indent=2, default=str)}

Provide a COMPREHENSIVE analysis in this exact JSON format:

{{
  "reverse_engineering_analysis": {{
    "business_domain_identification": {{
      "primary_domain": "e-commerce",
      "sub_domains": ["customer_management", "order_processing", "product_catalog"],
      "confidence_score": 95,
      "domain_evidence": ["Table names like 'orders', 'customers'", "Foreign key relationships"],
      "business_processes": ["Customer registration", "Order placement", "Product management"]
    }},
    "data_model_architecture": {{
      "design_pattern": "Entity-Relationship Model",
      "normalization_level": "3NF",
      "architectural_style": "Traditional Relational",
      "flexibility_score": 75,
      "scalability_indicators": ["Proper indexing", "Normalized structure"]
    }},
    "entity_relationship_mapping": {{
      "core_entities": [
        {{
          "entity_name": "Customer",
          "table_name": "customers",
          "key_attributes": ["customer_id", "email"],
          "business_purpose": "Store customer information and track customer behavior",
          "data_volume": "Medium",
          "update_frequency": "Low"
        }}
      ],
      "relationships": [
        {{
          "relationship_name": "Customer-Orders",
          "parent_entity": "Customer",
          "child_entity": "Order", 
          "relationship_type": "one-to-many",
          "business_meaning": "A customer can place multiple orders",
          "cardinality": "1:N",
          "foreign_key": "orders.customer_id -> customers.customer_id"
        }}
      ],
      "entity_hierarchy": {{
        "master_entities": ["Customer", "Product"],
        "transaction_entities": ["Order", "OrderItem"],
        "reference_entities": ["Category", "Status"]
      }}
    }}
  }},
  "metadata_extraction": {{
    "table_purposes": {{
      "customers": "Primary customer data storage with contact and behavioral information",
      "orders": "Order transaction records with financial and status tracking",
      "products": "Product catalog with pricing and inventory information"
    }},
    "column_semantics": {{
      "customer_id": "Primary identifier for customer records",
      "email": "Unique customer contact and login identifier", 
      "order_id": "Primary identifier for order transactions",
      "total_price": "Monetary value representing order total"
    }},
    "data_patterns": {{
      "identifier_patterns": ["Auto-incrementing IDs", "UUID patterns"],
      "naming_conventions": ["snake_case for tables", "camelCase for some columns"],
      "data_type_patterns": ["DECIMAL for monetary values", "TIMESTAMP for dates"]
    }},
    "business_rules_inferred": [
      "Customers must have unique email addresses",
      "Orders must be associated with valid customers",
      "Products have fixed pricing structure"
    ]
  }},
  "data_quality_assessment": {{
    "integrity_analysis": {{
      "referential_integrity": "Well-maintained with foreign key constraints",
      "data_consistency": "High - proper normalization",
      "completeness_score": 85,
      "accuracy_indicators": ["Proper data types", "Constraint enforcement"]
    }},
    "quality_issues": [
      "Potential missing indexes on frequently queried columns",
      "Some nullable fields that should be required"
    ],
    "data_governance": {{
      "pii_handling": "Email addresses stored - consider encryption",
      "audit_trail": "Basic timestamp tracking available",
      "data_retention": "No explicit retention policies visible"
    }}
  }},
  "performance_analysis": {{
    "query_patterns": [
      "Customer order history lookups",
      "Product catalog browsing with filtering",
      "Order status tracking and updates"
    ],
    "bottleneck_identification": [
      "Large table scans without proper indexing",
      "Complex joins on unindexed foreign keys"
    ],
    "optimization_opportunities": [
      "Add composite indexes for common query patterns",
      "Implement query result caching",
      "Consider read replicas for reporting"
    ],
    "scalability_assessment": {{
      "current_capacity": "Medium scale - suitable for small to medium business",
      "scaling_challenges": ["Single database instance", "Limited partitioning"],
      "scaling_recommendations": ["Implement sharding strategy", "Add caching layer"]
    }}
  }},
  "use_case_analysis": {{
    "primary_use_cases": [
      {{
        "use_case": "Customer Management",
        "description": "Complete customer lifecycle from registration to order history",
        "data_entities": ["Customer", "Order"],
        "business_value": "Customer relationship management and analytics"
      }},
      {{
        "use_case": "Order Processing", 
        "description": "End-to-end order management from creation to fulfillment",
        "data_entities": ["Order", "OrderItem", "Product"],
        "business_value": "Revenue tracking and operational efficiency"
      }}
    ],
    "analytics_opportunities": [
      "Customer behavior analysis",
      "Sales performance tracking", 
      "Product popularity metrics",
      "Revenue trend analysis"
    ],
    "integration_points": [
      "Payment gateway integration",
      "Inventory management system",
      "Customer support system",
      "Marketing automation platform"
    ]
  }},
  "technical_debt_assessment": {{
    "immediate_concerns": [
      "Missing indexes on foreign keys",
      "No explicit data validation constraints"
    ],
    "medium_term_improvements": [
      "Implement comprehensive audit logging",
      "Add data archiving strategy"
    ],
    "long_term_considerations": [
      "Microservices architecture migration",
      "Event-driven data architecture"
    ]
  }},
  "migration_insights": {{
    "complexity_assessment": "Medium complexity - well-structured but needs optimization",
    "migration_effort": "2-3 months for complete migration",
    "risk_factors": ["Data volume", "Downtime requirements"],
    "migration_strategy": "Phased migration with parallel systems"
  }}
}}

Focus on providing DEEP INSIGHTS that would help engineers understand the data model, business logic, and potential use cases without manual exploration. Be specific about relationships, data patterns, and business rules inferred from the schema structure.
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
