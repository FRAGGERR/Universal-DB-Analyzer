#!/usr/bin/env python3
"""
Consolidated Report Generator
Combines all analysis results into a single comprehensive output file
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3

class ConsolidatedReportGenerator:
    """Generates a single consolidated report combining all analysis results"""
    
    def __init__(self, output_dir: str = "consolidated_analysis"):
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_consolidated_report(self, db_path: str, db_name: str, 
                                   analysis_results: Dict[str, Any],
                                   graph_files: Dict[str, str]) -> str:
        """Generate a single consolidated report combining all analysis"""
        
        print(f"📋 Generating consolidated report for {db_name}...")
        
        # Extract key information
        analysis = analysis_results.get('analysis', {})
        reverse_eng = analysis.get('reverse_engineering_analysis', {})
        
        # Copy graph files to consolidated analysis folder for embedding
        embedded_graph_files = self._copy_graphs_for_embedding(db_name, graph_files)
        
        # Create comprehensive report
        report_content = self._create_report_content(db_name, db_path, analysis, reverse_eng, embedded_graph_files)
        
        # Save as Markdown
        md_filename = f"{self.output_dir}/{db_name}_consolidated_analysis.md"
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Save as JSON (structured data)
        json_filename = f"{self.output_dir}/{db_name}_consolidated_analysis.json"
        consolidated_data = self._create_consolidated_json(db_name, db_path, analysis, reverse_eng, embedded_graph_files)
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        
        # Generate HTML version with embedded graphs
        html_filename = self._create_html_report(db_name, db_path, analysis, reverse_eng, embedded_graph_files)
        
        print(f"✅ Consolidated report generated:")
        print(f"   📄 Markdown: {md_filename}")
        print(f"   📊 JSON: {json_filename}")
        print(f"   🌐 HTML: {html_filename}")
        
        return md_filename
    
    def _create_report_content(self, db_name: str, db_path: str, 
                              analysis: Dict[str, Any], 
                              reverse_eng: Dict[str, Any],
                              graph_files: Dict[str, str]) -> str:
        """Create comprehensive Markdown report content"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""# 🎯 {db_name.title()} Database - Consolidated Analysis Report

**Generated:** {timestamp}  
**Database File:** {db_path}  
**Analysis Type:** Comprehensive AI-Powered Database Reverse Engineering

---

## 📊 Executive Summary

This consolidated report provides a complete analysis of the **{db_name}** database, combining AI-powered insights, schema analysis, performance recommendations, and visual representations into a single comprehensive document.

---

## 🏢 Business Domain Analysis

### Primary Domain
- **Domain:** {reverse_eng.get('business_domain_identification', {}).get('primary_domain', 'Unknown')}
- **Confidence:** {reverse_eng.get('business_domain_identification', {}).get('confidence_score', 0)}%
- **Sub-domains:** {', '.join(reverse_eng.get('business_domain_identification', {}).get('sub_domains', []))}

### Business Processes
{self._format_list(reverse_eng.get('business_domain_identification', {}).get('business_processes', []))}

---

## 🏗️ Data Model Architecture

### Design Characteristics
- **Architectural Style:** {reverse_eng.get('data_model_architecture', {}).get('architectural_style', 'Unknown')}
- **Design Pattern:** {reverse_eng.get('data_model_architecture', {}).get('design_pattern', 'Unknown')}
- **Normalization Level:** {reverse_eng.get('data_model_architecture', {}).get('normalization_level', 'Unknown')}
- **Flexibility Score:** {reverse_eng.get('data_model_architecture', {}).get('flexibility_score', 0)}/100

### Schema Overview
{self._get_schema_overview(db_path)}

---

## 🎪 Core Entities & Relationships

### Primary Entities
{self._format_entities(reverse_eng.get('entity_relationship_mapping', {}).get('core_entities', []))}

### Key Relationships
{self._format_relationships(reverse_eng.get('entity_relationship_mapping', {}).get('relationships', []))}

---

## 📊 Data Quality Assessment

### Integrity Analysis
- **Referential Integrity:** {analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('referential_integrity', 'Unknown')}
- **Data Consistency:** {analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('data_consistency', 'Unknown')}
- **Completeness Score:** {analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('completeness_score', 0)}/100

### Accuracy Indicators
{self._format_list(analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('accuracy_indicators', []))}

---

## ⚡ Performance Analysis

### Query Patterns
{self._format_list(analysis.get('performance_analysis', {}).get('query_patterns', []))}

### Identified Bottlenecks
{self._format_list(analysis.get('performance_analysis', {}).get('bottleneck_identification', []))}

### Optimization Opportunities
{self._format_list(analysis.get('performance_analysis', {}).get('optimization_opportunities', []))}

---

## 🎯 Use Case Analysis

### Primary Use Cases
{self._format_use_cases(analysis.get('use_case_analysis', {}).get('primary_use_cases', []))}

### Analytics Opportunities
{self._format_list(analysis.get('use_case_analysis', {}).get('analytics_opportunities', []))}

---

## 🔄 Migration & Integration Insights

### Complexity Assessment
- **Migration Complexity:** {analysis.get('migration_insights', {}).get('complexity_assessment', 'Unknown')}
- **Effort Estimate:** {analysis.get('migration_insights', {}).get('migration_effort', 'Unknown')}

### Integration Recommendations
{self._format_list(analysis.get('migration_insights', {}).get('integration_recommendations', []))}

---

## 📈 Generated Visualizations

### Available Graphs
{self._format_graph_files(graph_files)}

### Graph Descriptions
- **Schema Overview:** Complete database structure visualization
- **Entity Relationship:** Table relationships and dependencies
- **Table Sizes:** Data volume distribution across tables
- **Data Types:** Column type analysis and distribution
- **Index Analysis:** Index coverage and optimization insights
- **Foreign Keys:** Relationship constraints and actions
- **Business Domain:** AI-extracted business insights
- **Performance:** Bottleneck identification and optimization

---

## 🚀 Recommendations & Next Steps

### Immediate Actions (1-2 weeks)
1. **Performance Optimization:** Implement identified missing indexes
2. **Data Quality:** Address any data consistency issues
3. **Monitoring:** Set up performance monitoring for identified bottlenecks

### Short-term Improvements (1-2 months)
1. **Query Optimization:** Refactor slow queries based on analysis
2. **Index Strategy:** Implement composite indexes for common join patterns
3. **Data Validation:** Add constraints and validation rules

### Long-term Considerations (3-6 months)
1. **Architecture Review:** Consider modernization opportunities
2. **Scalability Planning:** Design for future growth
3. **Integration Strategy:** Plan for system integration needs

---

## 📋 Technical Details

### Database Information
- **File Path:** {db_path}
- **File Size:** {self._get_file_size(db_path)}
- **Analysis Timestamp:** {timestamp}
- **Generated Graphs:** {len(graph_files)} visualizations

### Analysis Components
- ✅ Schema Extraction & Analysis
- ✅ AI-Powered Business Logic Extraction
- ✅ Performance Bottleneck Identification
- ✅ Data Quality Assessment
- ✅ Use Case Analysis
- ✅ Migration Planning
- ✅ Visual Graph Generation

---

## 🔍 How to Use This Report

1. **Review Executive Summary** for high-level understanding
2. **Examine Business Domain** to understand the data's purpose
3. **Study Architecture** to understand the design patterns
4. **Review Performance Analysis** for optimization opportunities
5. **Check Recommendations** for actionable next steps
6. **View Generated Graphs** for visual insights

---

*This report was automatically generated using AI-powered database analysis technology.  
For questions or additional analysis, refer to the detailed JSON data or individual graph files.*
"""
        
        return content
    
    def _create_consolidated_json(self, db_name: str, db_path: str,
                                  analysis: Dict[str, Any],
                                  reverse_eng: Dict[str, Any],
                                  graph_files: Dict[str, str]) -> Dict[str, Any]:
        """Create consolidated JSON data structure"""
        
        return {
            "metadata": {
                "database_name": db_name,
                "file_path": db_path,
                "analysis_timestamp": datetime.now().isoformat(),
                "file_size_bytes": self._get_file_size(db_path),
                "generated_graphs": len(graph_files)
            },
            "business_analysis": {
                "domain": reverse_eng.get('business_domain_identification', {}),
                "architecture": reverse_eng.get('data_model_architecture', {}),
                "entities": reverse_eng.get('entity_relationship_mapping', {}),
                "use_cases": analysis.get('use_case_analysis', {}),
                "migration": analysis.get('migration_insights', {})
            },
            "technical_analysis": {
                "data_quality": analysis.get('data_quality_assessment', {}),
                "performance": analysis.get('performance_analysis', {}),
                "schema": self._get_schema_data(db_path)
            },
            "visualizations": {
                "available_graphs": list(graph_files.keys()),
                "graph_files": graph_files
            },
            "recommendations": {
                "immediate_actions": [
                    "Implement missing indexes",
                    "Address data quality issues",
                    "Set up performance monitoring"
                ],
                "short_term": [
                    "Query optimization",
                    "Index strategy implementation",
                    "Data validation rules"
                ],
                "long_term": [
                    "Architecture modernization",
                    "Scalability planning",
                    "Integration strategy"
                ]
            }
        }
    
    def _create_html_report(self, db_name: str, db_path: str,
                           analysis: Dict[str, Any],
                           reverse_eng: Dict[str, Any],
                           graph_files: Dict[str, str]) -> str:
        """Create HTML version of the consolidated report"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{db_name.title()} Database - Consolidated Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            padding: 10px 0;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #2980b9;
            margin-top: 25px;
        }}
        .summary-box {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
            padding: 8px 15px;
            background-color: #3498db;
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }}
        .graph-section {{
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #fafafa;
        }}
        .graph-section img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .recommendation {{
            background-color: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #27ae60;
        }}
        .warning {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #ffc107;
        }}
        .info {{
            background-color: #d1ecf1;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #17a2b8;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 2px 5px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 {db_name.title()} Database - Consolidated Analysis Report</h1>
        
        <div class="summary-box">
            <h3>📊 Analysis Summary</h3>
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Database File:</strong> {db_path}</p>
            <p><strong>Analysis Type:</strong> Comprehensive AI-Powered Database Reverse Engineering</p>
        </div>
        
        <h2>🏢 Business Domain Analysis</h2>
        <div class="metric">Domain: {reverse_eng.get('business_domain_identification', {}).get('primary_domain', 'Unknown')}</div>
        <div class="metric">Confidence: {reverse_eng.get('business_domain_identification', {}).get('confidence_score', 0)}%</div>
        
        <h3>Business Processes</h3>
        <ul>
            {self._format_html_list(reverse_eng.get('business_domain_identification', {}).get('business_processes', []))}
        </ul>
        
        <h2>🏗️ Data Model Architecture</h2>
        <div class="metric">Style: {reverse_eng.get('data_model_architecture', {}).get('architectural_style', 'Unknown')}</div>
        <div class="metric">Pattern: {reverse_eng.get('data_model_architecture', {}).get('design_pattern', 'Unknown')}</div>
        <div class="metric">Flexibility: {reverse_eng.get('data_model_architecture', {}).get('flexibility_score', 0)}/100</div>
        
        <h2>🎪 Core Entities</h2>
        {self._format_html_entities(reverse_eng.get('entity_relationship_mapping', {}).get('core_entities', []))}
        
        <h2>📊 Data Quality Assessment</h2>
        <div class="info">
            <strong>Completeness Score:</strong> {analysis.get('data_quality_assessment', {}).get('integrity_analysis', {}).get('completeness_score', 0)}/100
        </div>
        
        <h2>⚡ Performance Analysis</h2>
        <div class="warning">
            <strong>Bottlenecks Identified:</strong> {len(analysis.get('performance_analysis', {}).get('bottleneck_identification', []))}
        </div>
        
        <h2>🎯 Use Cases</h2>
        {self._format_html_use_cases(analysis.get('use_case_analysis', {}).get('primary_use_cases', []))}
        
        <h2>📈 Generated Visualizations</h2>
        <p>This analysis generated <strong>{len(graph_files)} comprehensive graphs</strong> providing visual insights into:</p>
        <ul>
            <li>Database schema and structure</li>
            <li>Entity relationships and dependencies</li>
            <li>Data distribution and patterns</li>
            <li>Performance characteristics</li>
            <li>Business domain insights</li>
        </ul>
        
        <h2>🚀 Recommendations</h2>
        <div class="recommendation">
            <h3>Immediate Actions (1-2 weeks)</h3>
            <ul>
                <li>Implement missing indexes for performance</li>
                <li>Address any data quality issues</li>
                <li>Set up performance monitoring</li>
            </ul>
        </div>
        
        <div class="recommendation">
            <h3>Short-term Improvements (1-2 months)</h3>
            <ul>
                <li>Query optimization based on analysis</li>
                <li>Implement comprehensive index strategy</li>
                <li>Add data validation rules</li>
            </ul>
        </div>
        
        <div class="timestamp">
            <p>Report generated on {timestamp}</p>
            <p><em>This report combines AI-powered analysis with comprehensive visualizations for complete database understanding.</em></p>
        </div>
    </div>
</body>
</html>
        """
        
        # Save HTML report
        html_filename = f"{self.output_dir}/{db_name}_consolidated_analysis.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_filename
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items for Markdown"""
        if not items:
            return "- No items identified"
        return "\n".join([f"- {item}" for item in items])
    
    def _format_html_list(self, items: List[str]) -> str:
        """Format a list of items for HTML"""
        if not items:
            return "<li>No items identified</li>"
        return "\n".join([f"<li>{item}</li>" for item in items])
    
    def _format_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format entities for Markdown"""
        if not entities:
            return "No entities identified"
        
        result = []
        for entity in entities:
            result.append(f"**{entity.get('entity_name', 'Unknown')}** ({entity.get('table_name', 'Unknown')})")
            result.append(f"  - Purpose: {entity.get('business_purpose', 'Unknown')}")
            result.append(f"  - Data Volume: {entity.get('data_volume', 'Unknown')}")
            result.append("")
        
        return "\n".join(result)
    
    def _format_html_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format entities for HTML"""
        if not entities:
            return "<p>No entities identified</p>"
        
        result = ["<ul>"]
        for entity in entities:
            result.append(f"<li><strong>{entity.get('entity_name', 'Unknown')}</strong> ({entity.get('table_name', 'Unknown')})")
            result.append(f"<br>Purpose: {entity.get('business_purpose', 'Unknown')}")
            result.append(f"<br>Data Volume: {entity.get('data_volume', 'Unknown')}</li>")
        result.append("</ul>")
        
        return "\n".join(result)
    
    def _format_relationships(self, relationships: List[Dict[str, Any]]) -> str:
        """Format relationships for Markdown"""
        if not relationships:
            return "No relationships identified"
        
        result = []
        for rel in relationships:
            result.append(f"**{rel.get('parent_entity', 'Unknown')} ↔ {rel.get('child_entity', 'Unknown')}** ({rel.get('relationship_type', 'Unknown')})")
            result.append(f"  - Meaning: {rel.get('business_meaning', 'Unknown')}")
            result.append("")
        
        return "\n".join(result)
    
    def _format_use_cases(self, use_cases: List[Dict[str, Any]]) -> str:
        """Format use cases for Markdown"""
        if not use_cases:
            return "No use cases identified"
        
        result = []
        for uc in use_cases:
            result.append(f"**{uc.get('use_case', 'Unknown')}**")
            result.append(f"  - Description: {uc.get('description', 'No description')}")
            result.append(f"  - Business Value: {uc.get('business_value', 'Unknown')}")
            result.append("")
        
        return "\n".join(result)
    
    def _format_html_use_cases(self, use_cases: List[Dict[str, Any]]) -> str:
        """Format use cases for HTML"""
        if not use_cases:
            return "<p>No use cases identified</p>"
        
        result = ["<ul>"]
        for uc in use_cases:
            result.append(f"<li><strong>{uc.get('use_case', 'Unknown')}</strong>")
            result.append(f"<br>Description: {uc.get('description', 'No description')}")
            result.append(f"<br>Business Value: {uc.get('business_value', 'Unknown')}</li>")
        result.append("</ul>")
        
        return "\n".join(result)
    
    def _copy_graphs_for_embedding(self, db_name: str, graph_files: Dict[str, str]) -> Dict[str, str]:
        """Copy graph files to consolidated analysis folder for embedding in markdown"""
        if not graph_files:
            return {}
        
        embedded_graphs = {}
        graphs_dir = f"{self.output_dir}/{db_name}_graphs"
        os.makedirs(graphs_dir, exist_ok=True)
        
        for graph_type, original_path in graph_files.items():
            if original_path and os.path.exists(original_path):
                # Copy graph file to consolidated analysis folder
                filename = os.path.basename(original_path)
                new_path = os.path.join(graphs_dir, filename)
                
                try:
                    import shutil
                    shutil.copy2(original_path, new_path)
                    embedded_graphs[graph_type] = new_path
                    print(f"   📊 Copied {graph_type} graph: {filename}")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not copy {graph_type} graph: {e}")
                    # Keep original path if copy fails
                    embedded_graphs[graph_type] = original_path
        
        return embedded_graphs
    
    def _format_graph_files(self, graph_files: Dict[str, str]) -> str:
        """Format graph files for Markdown with embedded images"""
        if not graph_files:
            return "No graphs generated"
        
        result = []
        for graph_type, filepath in graph_files.items():
            if filepath and os.path.exists(filepath):
                filename = os.path.basename(filepath)
                # Create relative path for markdown embedding
                relative_path = f"./{os.path.basename(os.path.dirname(filepath))}/{filename}"
                result.append(f"- **{graph_type.replace('_', ' ').title()}:** {filename}")
                result.append(f"![{graph_type.replace('_', ' ').title()}]({relative_path})")
                result.append("")  # Add empty line for better markdown formatting
        
        return "\n".join(result)
    
    def _get_schema_overview(self, db_path: str) -> str:
        """Get schema overview information"""
        try:
            conn = sqlite3.connect(db_path)
            
            # Get table information
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            if tables.empty:
                return "No tables found"
            
            result = []
            for table_name in tables['name']:
                # Get column count
                cols_query = f"PRAGMA table_info(`{table_name}`)"
                cols = pd.read_sql_query(cols_query, conn)
                
                # Get row count
                try:
                    count_query = f"SELECT COUNT(*) as count FROM `{table_name}`"
                    count = pd.read_sql_query(count_query, conn)
                    row_count = count['count'].iloc[0]
                except:
                    row_count = 0
                
                result.append(f"- **{table_name}:** {len(cols)} columns, {row_count:,} rows")
            
            conn.close()
            return "\n".join(result)
            
        except Exception as e:
            return f"Error retrieving schema: {e}"
    
    def _get_schema_data(self, db_path: str) -> Dict[str, Any]:
        """Get structured schema data"""
        try:
            conn = sqlite3.connect(db_path)
            
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            schema_data = {}
            for table_name in tables['name']:
                # Get column information
                cols_query = f"PRAGMA table_info(`{table_name}`)"
                cols = pd.read_sql_query(cols_query, conn)
                
                # Get row count
                try:
                    count_query = f"SELECT COUNT(*) as count FROM `{table_name}`"
                    count = pd.read_sql_query(count_query, conn)
                    row_count = count['count'].iloc[0]
                except:
                    row_count = 0
                
                schema_data[table_name] = {
                    "columns": len(cols),
                    "rows": row_count,
                    "column_details": cols.to_dict('records')
                }
            
            conn.close()
            return schema_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_file_size(self, file_path: str) -> str:
        """Get file size in human readable format"""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
