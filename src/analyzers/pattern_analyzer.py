import google.generativeai as genai
import json
import logging
from typing import Dict, Any, List, Set
from dataclasses import dataclass

@dataclass
class GeminiConfig:
    api_key: str
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.1
    max_output_tokens: int = 8192

class PatternAnalyzer:
    """
    Specialized analyzer for finding patterns across multiple databases of the same domain.
    Identifies common entities, relationships, naming conventions, and integration opportunities.
    """

    def __init__(self, gemini_config: GeminiConfig):
        self.config = gemini_config
        self.logger = logging.getLogger(__name__)
        
        genai.configure(api_key=gemini_config.api_key)
        self.model = genai.GenerativeModel(
            model_name=gemini_config.model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=gemini_config.temperature,
                max_output_tokens=gemini_config.max_output_tokens,
            )
        )

    def analyze_common_patterns(self, databases_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze common patterns across multiple databases of the same business domain.
        
        Args:
            databases_analysis: Dict containing analysis results from multiple databases
            
        Returns:
            Dict containing pattern analysis results including common entities, 
            implementation differences, and integration opportunities
        """
        try:
            prompt = self._build_pattern_analysis_prompt(databases_analysis)
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            self.logger.error(f"Pattern analysis error: {e}")
            return self._create_error_response(str(e))

    def identify_entity_mappings(self, databases_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create entity mapping between different database implementations.
        """
        mapping_prompt = f"""
Analyze these database analyses and create entity mappings between different implementations:

Database Analyses:
{json.dumps(databases_analysis, indent=2, default=str)}


Create a mapping showing how the same business concept is implemented differently:

{{
  "entity_mappings": [
    {{
      "business_concept": "Customer",
      "implementations": {{
        "database1": {{"table": "customers", "key_fields": ["customer_id", "email"]}},
        "database2": {{"table": "users", "key_fields": ["user_id", "email_address"]}},
        "database3": {{"table": "wp_users", "key_fields": ["ID", "user_email"]}}
      }},
      "common_attributes": ["email", "name", "created_date"],
      "unique_attributes": {{
        "database1": ["loyalty_points", "preferred_store"],
        "database2": ["last_login", "avatar_url"]
      }},
      "standardization_recommendation": "Use 'customer' as standard entity name with 'customer_id' and 'email' as key fields"
    }}
  ],
  "field_mappings": [
    {{
      "concept": "Email Address",
      "variations": ["email", "email_address", "user_email", "customer_email"],
      "recommended_standard": "email",
      "data_type_variations": ["VARCHAR(255)", "TEXT", "VARCHAR(100)"],
      "recommended_type": "VARCHAR(255)"
    }}
  ]
}}

Focus on practical mapping for data migration and integration.
        """
        try:
            response = self.model.generate_content(mapping_prompt)
            return self._parse_response(response.text)
        except Exception as e:
            self.logger.error(f"Entity mapping error: {e}")
            return {"error": str(e)}

    def analyze_architecture_patterns(self, databases_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze architectural patterns and design decisions across databases.
        """
        arch_prompt = f"""
Analyze the architectural patterns and design decisions in these database implementations:

Database Analyses:
{json.dumps(databases_analysis, indent=2, default=str)}


Provide analysis focusing on:

{{
  "architectural_patterns": {{
    "normalization_approaches": {{
      "traditional_relational": ["databases using 3NF approach"],
      "eav_model": ["databases using Entity-Attribute-Value"],
      "document_oriented": ["databases with document/JSON storage"],
      "hybrid_approaches": ["databases mixing multiple patterns"]
    }},
    "scalability_strategies": {{
      "horizontal_scaling_ready": ["databases designed for sharding"],
      "vertical_scaling_optimized": ["databases optimized for single server"],
      "cache_friendly": ["databases with denormalized structures for caching"]
    }},
    "flexibility_vs_structure": {{
      "highly_structured": ["rigid schema databases"],
      "flexible_schema": ["databases allowing schema evolution"],
      "meta_driven": ["databases using metadata tables"]
    }}
  }},
  "design_philosophy": {{
    "data_integrity_focus": "Which databases prioritize referential integrity",
    "performance_focus": "Which databases prioritize query performance",
    "flexibility_focus": "Which databases prioritize schema flexibility",
    "simplicity_focus": "Which databases prioritize simplicity"
  }},
  "evolution_readiness": {{
    "easy_to_modify": ["databases that can evolve easily"],
    "migration_friendly": ["databases with good migration paths"],
    "backward_compatible": ["databases maintaining compatibility"]
  }}
}}
        """
        try:
            response = self.model.generate_content(arch_prompt)
            return self._parse_response(response.text)
        except Exception as e:
            self.logger.error(f"Architecture analysis error: {e}")
            return {"error": str(e)}

    def generate_integration_strategy(self, databases_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate integration strategies and recommendations.
        """
        integration_prompt = f"""
Based on these database analyses, create a comprehensive integration strategy:

Database Analyses:
{json.dumps(databases_analysis, indent=2, default=str)}


Provide detailed integration strategy:

{{
  "integration_approaches": [
    {{
      "approach": "API Gateway Pattern",
      "description": "Unified API layer over multiple databases",
      "best_for": ["real-time integration", "maintaining database independence"],
      "complexity": "medium",
      "implementation_steps": ["step1", "step2", "step3"]
    }},
    {{
      "approach": "Data Lake/Warehouse",
      "description": "Centralized data repository",
      "best_for": ["analytics", "reporting", "data science"],
      "complexity": "high",
      "implementation_steps": ["step1", "step2", "step3"]
    }}
  ],
  "migration_paths": [
    {{
      "from": "database1",
      "to": "database2",
      "complexity": "medium",
      "estimated_effort": "4-6 weeks",
      "key_challenges": ["schema transformation", "data validation"],
      "migration_strategy": "ETL with validation checkpoints",
      "rollback_plan": "maintain parallel systems during transition"
    }}
  ],
  "data_synchronization": {{
    "real_time_sync": {{
      "recommended_tools": ["Apache Kafka", "AWS DMS"],
      "sync_patterns": ["event-driven", "CDC (Change Data Capture)"],
      "conflict_resolution": "last-write-wins with business rule exceptions"
    }},
    "batch_sync": {{
      "recommended_schedule": "nightly for non-critical data",
      "validation_strategy": "checksums and row counts",
      "error_handling": "quarantine and manual review"
    }}
  }},
  "unified_schema_design": {{
    "recommended_entities": ["Customer", "Product", "Order", "Transaction"],
    "common_fields": {{
      "Customer": ["id", "email", "name", "created_at", "updated_at"],
      "Product": ["id", "sku", "name", "price", "category"]
    }},
    "extensibility_strategy": "JSON fields for platform-specific attributes"
  }}
}}
        """
        try:
            response = self.model.generate_content(integration_prompt)
            return self._parse_response(response.text)
        except Exception as e:
            self.logger.error(f"Integration strategy error: {e}")
            return {"error": str(e)}

    def compare_performance_characteristics(self, databases_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare performance characteristics and optimization strategies.
        """
        perf_prompt = f"""
Compare performance characteristics across these database implementations:

Database Analyses:
{json.dumps(databases_analysis, indent=2, default=str)}


Analyze and compare:

{{
  "indexing_strategies": {{
    "well_indexed": ["databases with comprehensive indexing"],
    "under_indexed": ["databases missing critical indexes"],
    "over_indexed": ["databases with potentially excessive indexes"],
    "best_practices": ["common indexing patterns across implementations"]
  }},
  "query_optimization": {{
    "optimized_for_reads": ["databases optimized for SELECT operations"],
    "optimized_for_writes": ["databases optimized for INSERT/UPDATE"],
    "balanced_approach": ["databases with balanced read/write optimization"],
    "potential_bottlenecks": ["identified performance bottlenecks"]
  }},
  "scalability_comparison": {{
    "horizontal_scaling": {{
      "ready": ["databases ready for horizontal scaling"],
      "needs_work": ["databases requiring changes for scaling"],
      "challenges": ["specific challenges for each database"]
    }},
    "vertical_scaling": {{
      "efficient": ["databases efficient on single server"],
      "resource_intensive": ["databases requiring significant resources"]
    }}
  }},
  "caching_opportunities": {{
    "cache_friendly_queries": ["common query patterns suitable for caching"],
    "cache_invalidation_strategies": ["recommended cache invalidation approaches"],
    "materialized_views": ["opportunities for materialized views"]
  }},
  "performance_recommendations": {{
    "immediate_wins": ["quick performance improvements"],
    "long_term_optimizations": ["strategic performance improvements"],
    "monitoring_metrics": ["key metrics to monitor"]
  }}
}}
        """
        try:
            response = self.model.generate_content(perf_prompt)
            return self._parse_response(response.text)
        except Exception as e:
            self.logger.error(f"Performance comparison error: {e}")
            return {"error": str(e)}

    def analyze_data_governance_patterns(self, databases_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data governance, security, and compliance patterns.
        """
        governance_prompt = f"""
Analyze data governance, security, and compliance patterns:

Database Analyses:
{json.dumps(databases_analysis, indent=2, default=str)}


Focus on:

{{
  "security_patterns": {{
    "pii_handling": {{
      "well_protected": ["databases with good PII protection"],
      "needs_improvement": ["databases with PII concerns"],
      "encryption_status": ["encryption implementation across databases"],
      "access_control": ["access control patterns"]
    }},
    "audit_trails": {{
      "comprehensive_logging": ["databases with good audit trails"],
      "minimal_logging": ["databases with limited audit capabilities"],
      "compliance_ready": ["databases ready for compliance audits"]
    }}
  }},
  "data_quality": {{
    "validation_rules": ["data validation patterns across databases"],
    "consistency_checks": ["data consistency mechanisms"],
    "data_cleansing": ["data quality maintenance approaches"]
  }},
  "compliance_readiness": {{
    "gdpr_compliance": {{
      "ready": ["GDPR-ready databases"],
      "needs_work": ["databases requiring GDPR improvements"],
      "right_to_erasure": ["implementation of data deletion"]
    }},
    "industry_standards": ["compliance with industry-specific standards"],
    "data_retention": ["data retention policies and implementation"]
  }},
  "governance_recommendations": {{
    "standardization_opportunities": ["areas for governance standardization"],
    "policy_enforcement": ["recommended policy enforcement mechanisms"],
    "monitoring_and_reporting": ["governance monitoring recommendations"]
  }}
}}
        """
        try:
            response = self.model.generate_content(governance_prompt)
            return self._parse_response(response.text)
        except Exception as e:
            self.logger.error(f"Data governance analysis error: {e}")
            return {"error": str(e)}

    # ----- Internal helper methods -----

    def _build_pattern_analysis_prompt(self, databases_analysis: Dict[str, Any]) -> str:
        """
        Build the main pattern analysis prompt for Gemini.
        """
        return f"""
You are analyzing multiple database implementations of the SAME BUSINESS DOMAIN to identify common patterns, shared attributes, and implementation differences.

Database Analyses:
{json.dumps(databases_analysis, indent=2, default=str)}


Please provide a comprehensive JSON analysis focusing on:

{{
  "domain_confirmation": {{
    "confirmed_domain": "The shared business domain across all databases",
    "confidence_score": 95,
    "domain_evidence": ["Evidence that confirms this domain"]
  }},
  "common_attributes": {{
    "shared_entities": [
      {{
        "entity_name": "Customer/User",
        "found_in_databases": ["db1", "db2", "db3"],
        "common_fields": ["email", "name", "created_date"],
        "implementation_variations": {{
          "db1": {{"table_name": "customers", "key_fields": ["customer_id", "email"]}},
          "db2": {{"table_name": "users", "key_fields": ["user_id", "email_address"]}}
        }}
      }}
    ],
    "shared_relationships": [
      {{
        "relationship": "Customer-Orders",
        "found_in_databases": ["db1", "db2"],
        "relationship_type": "one-to-many",
        "implementation_differences": ["Different foreign key naming", "Different status values"]
      }}
    ]
  }},
  "implementation_patterns": {{
    "naming_conventions": {{
      "consistent_patterns": ["snake_case for most databases"],
      "inconsistencies": ["user vs customer", "order_id vs order_number"],
      "recommendations": ["Standardize on 'customer' entity naming"]
    }},
    "data_types": {{
      "common_approaches": ["DECIMAL for monetary values", "TIMESTAMP for dates"],
      "variations": ["Different precision for decimals", "Date vs DateTime usage"],
      "best_practices": ["Use consistent decimal precision across platforms"]
    }},
    "indexing_strategies": {{
      "common_indexes": ["email indexes", "foreign key indexes"],
      "missing_opportunities": ["Composite indexes for queries", "Full-text search indexes"],
      "performance_insights": ["All databases index primary identifiers similarly"]
    }}
  }},
  "architectural_differences": {{
    "normalization_approaches": {{
      "database1": "3NF with traditional relational design",
      "database2": "EAV model for flexibility",
      "database3": "Denormalized for WordPress integration"
    }},
    "scalability_patterns": {{
      "horizontal_scaling": ["database1 uses sharding-friendly design"],
      "vertical_scaling": ["database2 optimized for single-server performance"],
      "hybrid_approaches": ["database3 uses caching-friendly structure"]
    }}
  }},
  "integration_opportunities": {{
    "data_standardization": [
      {{
        "area": "Customer Data",
        "current_variations": ["Different field names", "Different validation rules"],
        "standardization_approach": "Create unified customer schema",
        "effort_estimate": "medium"
      }}
    ],
    "api_unification": [
      {{
        "endpoint_type": "Customer Management",
        "common_operations": ["create", "update", "get", "list"],
        "implementation_differences": ["Different response formats", "Different error handling"],
        "unification_strategy": "GraphQL federation or REST API gateway"
      }}
    ],
    "data_migration_paths": [
      {{
        "from_platform": "database1",
        "to_platform": "database2", 
        "complexity": "medium",
        "key_challenges": ["Schema transformation", "Data type conversion"],
        "migration_strategy": "ETL pipeline with data validation"
      }}
    ]
  }},
  "best_practices_analysis": {{
    "security_patterns": {{
      "common_approaches": ["Password hashing", "Email validation"],
      "gaps_identified": ["Inconsistent PII handling", "Missing audit trails"],
      "recommendations": ["Implement consistent encryption", "Add comprehensive logging"]
    }},
    "performance_optimizations": {{
      "successful_patterns": ["Indexed foreign keys", "Efficient pagination"],
      "improvement_opportunities": ["Add query optimization", "Implement caching layers"],
      "scaling_recommendations": ["Consider read replicas", "Implement connection pooling"]
    }}
  }},
  "industry_insights": {{
    "standard_compliance": "How well do these implementations follow industry standards",
    "innovation_areas": ["Unique approaches that could be adopted by others"],
    "evolution_trends": ["How these schemas reflect industry evolution"]
  }}
}}

Focus specifically on finding commonalities and variations rather than analyzing each database in isolation.
        """

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini's JSON response with robust error handling.
        """
        try:
            response_text = response_text.strip()
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                return json.loads(json_text)
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text[:500]
            }

    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """
        Create standardized error response structure.
        """
        return {
            "error": error_msg,
            "domain_confirmation": {
                "confirmed_domain": "Unknown",
                "confidence_score": 0
            },
            "common_attributes": {
                "shared_entities": [],
                "shared_relationships": []
            },
            "integration_opportunities": {
                "data_standardization": [],
                "api_unification": [],
                "data_migration_paths": []
            }
        }

    def extract_naming_patterns(self, databases_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract and categorize naming patterns across databases.
        """
        patterns = {
            "table_naming": [],
            "column_naming": [],
            "id_patterns": [],
            "timestamp_patterns": [],
            "foreign_key_patterns": []
        }
        
        for db_name, analysis in databases_analysis.items():
            # Extract entity names from domain analysis
            entities = analysis.get('domain_analysis', {}).get('key_business_entities', [])
            patterns["table_naming"].extend(entities)
            
            # Extract relationship patterns
            relationships = analysis.get('relationship_analysis', {}).get('primary_relationships', [])
            for rel in relationships:
                if isinstance(rel, dict):
                    patterns["foreign_key_patterns"].append(rel.get('relationship_type', ''))
        
        return patterns

    def calculate_similarity_score(self, db1_analysis: Dict[str, Any], db2_analysis: Dict[str, Any]) -> float:
        """
        Calculate similarity score between two database analyses.
        """
        try:
            # Get entities from both databases
            entities1 = set(db1_analysis.get('domain_analysis', {}).get('key_business_entities', []))
            entities2 = set(db2_analysis.get('domain_analysis', {}).get('key_business_entities', []))
            
            # Calculate Jaccard similarity
            if not entities1 and not entities2:
                return 1.0  # Both empty
            
            intersection = len(entities1.intersection(entities2))
            union = len(entities1.union(entities2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {e}")
            return 0.0
