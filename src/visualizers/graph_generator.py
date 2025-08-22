#!/usr/bin/env python3
"""
Graph Generator for Database Analysis
Generates comprehensive visualizations for any database schema and data
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
from plotly.subplots import make_subplots
import networkx as nx
from typing import Dict, List, Any, Optional
import sqlite3
from pathlib import Path

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DatabaseGraphGenerator:
    """Generates comprehensive visualizations for database analysis"""
    
    def __init__(self, output_dir: str = "analysis_graphs"):
        self.output_dir = output_dir
        self.db_path = None
        self.analysis_data = None
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def set_database(self, db_path: str, analysis_data: Dict[str, Any] = None):
        """Set the database path and analysis data"""
        self.db_path = db_path
        self.analysis_data = analysis_data or {}
    
    def generate_all_graphs(self, db_name: str = "database") -> Dict[str, str]:
        """Generate all available graphs for the database"""
        if not self.db_path:
            raise ValueError("Database path not set. Call set_database() first.")
        
        print(f"🎨 Generating comprehensive graphs for {db_name}...")
        
        graph_files = {}
        
        try:
            # 1. Schema Overview Graph
            schema_file = self.generate_schema_overview(db_name)
            if schema_file:
                graph_files['schema_overview'] = schema_file
            
            # 2. Entity Relationship Diagram
            erd_file = self.generate_entity_relationship_diagram(db_name)
            if erd_file:
                graph_files['entity_relationship'] = erd_file
            
            # 3. Table Size Distribution
            size_file = self.generate_table_size_distribution(db_name)
            if size_file:
                graph_files['table_sizes'] = size_file
            
            # 4. Data Type Distribution
            type_file = self.generate_data_type_distribution(db_name)
            if type_file:
                graph_files['data_types'] = type_file
            
            # 5. Index Analysis
            index_file = self.generate_index_analysis(db_name)
            if index_file:
                graph_files['index_analysis'] = index_file
            
            # 6. Foreign Key Relationships
            fk_file = self.generate_foreign_key_analysis(db_name)
            if fk_file:
                graph_files['foreign_keys'] = fk_file
            
            # 7. Business Domain Analysis (if available)
            if self.analysis_data:
                domain_file = self.generate_business_domain_analysis(db_name)
                if domain_file:
                    graph_files['business_domain'] = domain_file
            
            # 8. Performance Insights
            perf_file = self.generate_performance_insights(db_name)
            if perf_file:
                graph_files['performance'] = perf_file
            
            print(f"✅ Generated {len(graph_files)} graph files in {self.output_dir}/")
            return graph_files
            
        except Exception as e:
            print(f"❌ Error generating graphs: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def generate_schema_overview(self, db_name: str) -> Optional[str]:
        """Generate schema overview visualization"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get table information
            tables_query = """
            SELECT name, sql FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
            tables = pd.read_sql_query(tables_query, conn)
            
            # Get column counts
            table_info = []
            for table_name in tables['name']:
                cols_query = f"PRAGMA table_info({table_name})"
                cols = pd.read_sql_query(cols_query, conn)
                table_info.append({
                    'table': table_name,
                    'columns': len(cols),
                    'primary_keys': len(cols[cols['pk'] > 0]),
                    'foreign_keys': len(cols[cols['name'].str.contains('_id', case=False)])
                })
            
            df = pd.DataFrame(table_info)
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'Schema Overview: {db_name}', fontsize=16, fontweight='bold')
            
            # 1. Column count by table
            axes[0, 0].bar(df['table'], df['columns'], color='skyblue', alpha=0.7)
            axes[0, 0].set_title('Columns per Table')
            axes[0, 0].set_xlabel('Table')
            axes[0, 0].set_ylabel('Column Count')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. Primary keys
            axes[0, 1].bar(df['table'], df['primary_keys'], color='lightgreen', alpha=0.7)
            axes[0, 1].set_title('Primary Keys per Table')
            axes[0, 1].set_xlabel('Table')
            axes[0, 1].set_ylabel('Primary Key Count')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Foreign keys
            axes[1, 0].bar(df['table'], df['foreign_keys'], color='lightcoral', alpha=0.7)
            axes[1, 0].set_title('Foreign Key Candidates per Table')
            axes[1, 0].set_xlabel('Table')
            axes[1, 0].set_ylabel('Foreign Key Count')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # 4. Table summary
            axes[1, 1].text(0.1, 0.9, f"Total Tables: {len(df)}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.8, f"Total Columns: {df['columns'].sum()}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.7, f"Total Primary Keys: {df['primary_keys'].sum()}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.6, f"Foreign Key Candidates: {df['foreign_keys'].sum()}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Database Summary')
            axes[1, 1].axis('off')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_schema_overview.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            return filename
            
        except Exception as e:
            print(f"Error generating schema overview: {e}")
            return None
    
    def generate_entity_relationship_diagram(self, db_name: str) -> Optional[str]:
        """Generate entity relationship diagram"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get foreign key information
            fk_query = """
            SELECT 
                m.name as table_name,
                p."from" as column_name,
                p."table" as referenced_table,
                p."to" as referenced_column
            FROM sqlite_master m
            JOIN pragma_foreign_key_list(m.name) p
            WHERE m.type = 'table'
            """
            
            try:
                foreign_keys = pd.read_sql_query(fk_query, conn)
            except:
                # Fallback for databases without foreign key constraints
                foreign_keys = pd.DataFrame(columns=['table_name', 'column_name', 'referenced_table', 'referenced_column'])
            
            # Create NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes (tables)
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            for table in tables['name']:
                G.add_node(table, node_type='table')
            
            # Add edges (relationships)
            for _, fk in foreign_keys.iterrows():
                G.add_edge(
                    fk['table_name'], 
                    fk['referenced_table'], 
                    relationship=fk['column_name'] + ' → ' + fk['referenced_column']
                )
            
            # Create the plot
            plt.figure(figsize=(16, 12))
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, 
                                  node_color='lightblue', 
                                  node_size=3000, 
                                  alpha=0.8)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, 
                                  edge_color='gray', 
                                  arrows=True, 
                                  arrowsize=20,
                                  alpha=0.6)
            
            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
            
            # Draw edge labels
            edge_labels = nx.get_edge_attributes(G, 'relationship')
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
            
            plt.title(f'Entity Relationship Diagram: {db_name}', fontsize=16, fontweight='bold')
            plt.axis('off')
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_entity_relationship.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            return filename
            
        except Exception as e:
            print(f"Error generating ERD: {e}")
            return None
    
    def generate_table_size_distribution(self, db_name: str) -> Optional[str]:
        """Generate table size distribution visualization"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get table sizes
            size_query = """
            SELECT 
                name as table_name,
                (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=table_name) as table_count
            FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """
            
            # Get actual row counts
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            table_sizes = []
            for table in tables['name']:
                try:
                    count_query = f"SELECT COUNT(*) as count FROM `{table}`"
                    count = pd.read_sql_query(count_query, conn)
                    table_sizes.append({
                        'table': table,
                        'row_count': count['count'].iloc[0]
                    })
                except:
                    table_sizes.append({'table': table, 'row_count': 0})
            
            df = pd.DataFrame(table_sizes)
            
            # Create visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle(f'Table Size Distribution: {db_name}', fontsize=16, fontweight='bold')
            
            # Bar chart
            bars = ax1.bar(df['table'], df['row_count'], color='lightgreen', alpha=0.7)
            ax1.set_title('Row Count by Table')
            ax1.set_xlabel('Table')
            ax1.set_ylabel('Row Count')
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{int(height):,}', ha='center', va='bottom')
            
            # Pie chart for top tables
            top_tables = df.nlargest(8, 'row_count')
            ax2.pie(top_tables['row_count'], labels=top_tables['table'], autopct='%1.1f%%', startangle=90)
            ax2.set_title('Top 8 Tables by Size')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_table_sizes.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            return filename
            
        except Exception as e:
            print(f"Error generating table size distribution: {e}")
            return None
    
    def generate_data_type_distribution(self, db_name: str) -> Optional[str]:
        """Generate data type distribution visualization"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get data types for all tables
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            data_types = []
            for table in tables['name']:
                try:
                    pragma_query = f"PRAGMA table_info(`{table}`)"
                    pragma = pd.read_sql_query(pragma_query, conn)
                    
                    for _, col in pragma.iterrows():
                        data_types.append({
                            'table': table,
                            'column': col['name'],
                            'type': col['type'].upper(),
                            'nullable': col['notnull'] == 0,
                            'primary_key': col['pk'] > 0
                        })
                except:
                    continue
            
            df = pd.DataFrame(data_types)
            
            if df.empty:
                return None
            
            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Data Type Distribution: {db_name}', fontsize=16, fontweight='bold')
            
            # 1. Data type counts
            type_counts = df['type'].value_counts()
            axes[0, 0].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%', startangle=90)
            axes[0, 0].set_title('Data Type Distribution')
            
            # 2. Nullable vs Not Nullable
            nullable_counts = df['nullable'].value_counts()
            axes[0, 1].bar(['Not Nullable', 'Nullable'], nullable_counts.values, color=['lightcoral', 'lightblue'])
            axes[0, 1].set_title('Nullable vs Not Nullable Columns')
            axes[0, 1].set_ylabel('Column Count')
            
            # 3. Primary keys
            pk_counts = df['primary_key'].value_counts()
            axes[1, 0].bar(['Not Primary Key', 'Primary Key'], pk_counts.values, color=['lightgray', 'gold'])
            axes[1, 0].set_title('Primary Key Distribution')
            axes[1, 0].set_ylabel('Column Count')
            
            # 4. Data types by table
            type_by_table = df.groupby(['table', 'type']).size().unstack(fill_value=0)
            type_by_table.plot(kind='bar', ax=axes[1, 1], stacked=True, alpha=0.7)
            axes[1, 1].set_title('Data Types by Table')
            axes[1, 1].set_xlabel('Table')
            axes[1, 1].set_ylabel('Column Count')
            axes[1, 1].tick_params(axis='x', rotation=45)
            axes[1, 1].legend(title='Data Type', bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_data_types.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            return filename
            
        except Exception as e:
            print(f"Error generating data type distribution: {e}")
            return None
    
    def generate_index_analysis(self, db_name: str) -> Optional[str]:
        """Generate index analysis visualization"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get index information
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            index_info = []
            for table in tables['name']:
                try:
                    # Get indexes for the table
                    index_query = f"PRAGMA index_list(`{table}`)"
                    indexes = pd.read_sql_query(index_query, conn)
                    
                    for _, idx in indexes.iterrows():
                        # Get index details
                        idx_detail_query = f"PRAGMA index_info(`{idx['name']}`)"
                        idx_detail = pd.read_sql_query(idx_detail_query, conn)
                        
                        index_info.append({
                            'table': table,
                            'index_name': idx['name'],
                            'unique': idx['unique'] == 1,
                            'columns': len(idx_detail)
                        })
                except:
                    continue
            
            df = pd.DataFrame(index_info)
            
            if df.empty:
                return None
            
            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Index Analysis: {db_name}', fontsize=16, fontweight='bold')
            
            # 1. Index count by table
            idx_by_table = df.groupby('table').size()
            axes[0, 0].bar(idx_by_table.index, idx_by_table.values, color='lightgreen', alpha=0.7)
            axes[0, 0].set_title('Index Count by Table')
            axes[0, 0].set_xlabel('Table')
            axes[0, 0].set_ylabel('Index Count')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. Unique vs Non-unique indexes
            unique_counts = df['unique'].value_counts()
            axes[0, 1].pie(unique_counts.values, labels=['Non-Unique', 'Unique'], autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('Unique vs Non-Unique Indexes')
            
            # 3. Index column count distribution
            col_counts = df['columns'].value_counts().sort_index()
            axes[1, 0].bar(col_counts.index, col_counts.values, color='lightcoral', alpha=0.7)
            axes[1, 0].set_title('Index Column Count Distribution')
            axes[1, 0].set_xlabel('Number of Columns')
            axes[1, 0].set_ylabel('Index Count')
            
            # 4. Summary statistics
            axes[1, 1].text(0.1, 0.9, f"Total Indexes: {len(df)}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.8, f"Unique Indexes: {len(df[df['unique']])}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.7, f"Tables with Indexes: {df['table'].nunique()}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.6, f"Avg Columns per Index: {df['columns'].mean():.1f}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Index Summary')
            axes[1, 1].axis('off')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_index_analysis.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            return filename
            
        except Exception as e:
            print(f"Error generating index analysis: {e}")
            return None
    
    def generate_foreign_key_analysis(self, db_name: str) -> Optional[str]:
        """Generate foreign key analysis visualization"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get foreign key information
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            fk_info = []
            for table in tables['name']:
                try:
                    fk_query = f"PRAGMA foreign_key_list(`{table}`)"
                    foreign_keys = pd.read_sql_query(fk_query, conn)
                    
                    for _, fk in foreign_keys.iterrows():
                        fk_info.append({
                            'source_table': table,
                            'source_column': fk['from'],
                            'target_table': fk['table'],
                            'target_column': fk['to'],
                            'on_update': fk['on_update'],
                            'on_delete': fk['on_delete']
                        })
                except:
                    continue
            
            df = pd.DataFrame(fk_info)
            
            if df.empty:
                return None
            
            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Foreign Key Analysis: {db_name}', fontsize=16, fontweight='bold')
            
            # 1. Foreign key count by table
            fk_by_table = df.groupby('source_table').size()
            axes[0, 0].bar(fk_by_table.index, fk_by_table.values, color='lightblue', alpha=0.7)
            axes[0, 0].set_title('Foreign Keys by Source Table')
            axes[0, 0].set_xlabel('Source Table')
            axes[0, 0].set_ylabel('Foreign Key Count')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. Referenced tables
            ref_by_table = df.groupby('target_table').size()
            axes[0, 1].bar(ref_by_table.index, ref_by_table.values, color='lightgreen', alpha=0.7)
            axes[0, 1].set_title('References by Target Table')
            axes[0, 1].set_xlabel('Target Table')
            axes[0, 1].set_ylabel('Reference Count')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. ON UPDATE actions
            update_actions = df['on_update'].value_counts()
            axes[1, 0].pie(update_actions.values, labels=update_actions.index, autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title('ON UPDATE Actions')
            
            # 4. ON DELETE actions
            delete_actions = df['on_delete'].value_counts()
            axes[1, 1].pie(delete_actions.values, labels=delete_actions.index, autopct='%1.1f%%', startangle=90)
            axes[1, 1].set_title('ON DELETE Actions')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_foreign_keys.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            return filename
            
        except Exception as e:
            print(f"Error generating foreign key analysis: {e}")
            return None
    
    def generate_business_domain_analysis(self, db_name: str) -> Optional[str]:
        """Generate business domain analysis visualization"""
        if not self.analysis_data:
            return None
        
        try:
            # Extract business domain information
            reverse_eng = self.analysis_data.get('reverse_engineering_analysis', {})
            domain_info = reverse_eng.get('business_domain_identification', {})
            
            if not domain_info:
                return None
            
            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Business Domain Analysis: {db_name}', fontsize=16, fontweight='bold')
            
            # 1. Confidence score
            confidence = domain_info.get('confidence_score', 0)
            axes[0, 0].pie([confidence, 100-confidence], labels=['Confidence', 'Uncertainty'], 
                           autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightgray'])
            axes[0, 0].set_title(f'Domain Confidence: {confidence}%')
            
            # 2. Sub-domains
            sub_domains = domain_info.get('sub_domains', [])
            if sub_domains:
                axes[0, 1].bar(range(len(sub_domains)), [1]*len(sub_domains), 
                               color='lightblue', alpha=0.7)
                axes[0, 1].set_title('Business Sub-domains')
                axes[0, 1].set_xticks(range(len(sub_domains)))
                axes[0, 1].set_xticklabels(sub_domains, rotation=45, ha='right')
                axes[0, 1].set_ylabel('Count')
            
            # 3. Business processes
            processes = domain_info.get('business_processes', [])
            if processes:
                axes[1, 0].bar(range(len(processes)), [1]*len(processes), 
                               color='lightcoral', alpha=0.7)
                axes[1, 0].set_title('Business Processes')
                axes[1, 0].set_xticks(range(len(processes)))
                axes[1, 0].set_xticklabels(processes, rotation=45, ha='right')
                axes[1, 0].set_ylabel('Count')
            
            # 4. Summary
            primary_domain = domain_info.get('primary_domain', 'Unknown')
            axes[1, 1].text(0.1, 0.9, f"Primary Domain: {primary_domain}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.8, f"Sub-domains: {len(sub_domains)}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.7, f"Processes: {len(processes)}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Domain Summary')
            axes[1, 1].axis('off')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_business_domain.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filename
            
        except Exception as e:
            print(f"Error generating business domain analysis: {e}")
            return None
    
    def generate_performance_insights(self, db_name: str) -> Optional[str]:
        """Generate performance insights visualization"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get table sizes for performance analysis
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            tables = pd.read_sql_query(tables_query, conn)
            
            perf_data = []
            for table in tables['name']:
                try:
                    # Get row count
                    count_query = f"SELECT COUNT(*) as count FROM `{table}`"
                    count = pd.read_sql_query(count_query, conn)
                    row_count = count['count'].iloc[0]
                    
                    # Get column count
                    pragma_query = f"PRAGMA table_info(`{table}`)"
                    pragma = pd.read_sql_query(pragma_query, conn)
                    col_count = len(pragma)
                    
                    # Get index count
                    index_query = f"PRAGMA index_list(`{table}`)"
                    indexes = pd.read_sql_query(index_query, conn)
                    index_count = len(indexes)
                    
                    perf_data.append({
                        'table': table,
                        'row_count': row_count,
                        'column_count': col_count,
                        'index_count': index_count,
                        'size_score': row_count * col_count,  # Rough size metric
                        'index_ratio': index_count / col_count if col_count > 0 else 0
                    })
                except:
                    continue
            
            df = pd.DataFrame(perf_data)
            
            if df.empty:
                return None
            
            # Create visualization
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Performance Insights: {db_name}', fontsize=16, fontweight='bold')
            
            # 1. Table size distribution
            axes[0, 0].scatter(df['column_count'], df['row_count'], s=df['index_count']*50, 
                               alpha=0.6, c=df['index_count'], cmap='viridis')
            axes[0, 0].set_xlabel('Column Count')
            axes[0, 0].set_ylabel('Row Count')
            axes[0, 0].set_title('Table Size vs Complexity (Bubble size = Index count)')
            
            # 2. Index coverage
            axes[0, 1].bar(df['table'], df['index_ratio'], color='lightgreen', alpha=0.7)
            axes[0, 1].set_title('Index Coverage Ratio (Indexes/Columns)')
            axes[0, 1].set_xlabel('Table')
            axes[0, 1].set_ylabel('Index Ratio')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Performance risk assessment
            df['risk_score'] = df['size_score'] * (1 - df['index_ratio'])
            high_risk = df[df['risk_score'] > df['risk_score'].quantile(0.8)]
            
            axes[1, 0].bar(high_risk['table'], high_risk['risk_score'], color='red', alpha=0.7)
            axes[1, 0].set_title('High Performance Risk Tables')
            axes[1, 0].set_xlabel('Table')
            axes[1, 0].set_ylabel('Risk Score')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # 4. Optimization recommendations
            axes[1, 1].text(0.1, 0.9, f"Tables Analyzed: {len(df)}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.8, f"High Risk Tables: {len(high_risk)}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.7, f"Avg Index Ratio: {df['index_ratio'].mean():.2f}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].text(0.1, 0.6, f"Total Rows: {df['row_count'].sum():,}", fontsize=12, transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Performance Summary')
            axes[1, 1].axis('off')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"{self.output_dir}/{db_name}_performance.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            conn.close()
            return filename
            
        except Exception as e:
            print(f"Error generating performance insights: {e}")
            return None
    
    def generate_html_report(self, db_name: str, graph_files: Dict[str, str]) -> str:
        """Generate an HTML report with all graphs"""
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Database Analysis Report - {db_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                    .graph-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .graph-section h3 {{ color: #2980b9; margin-top: 0; }}
                    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }}
                    .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .timestamp {{ text-align: center; color: #7f8c8d; font-style: italic; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎯 Database Analysis Report</h1>
                    <h2>Database: {db_name}</h2>
                    
                    <div class="summary">
                        <h3>📊 Analysis Summary</h3>
                        <p>This report contains comprehensive visualizations and insights for the <strong>{db_name}</strong> database.</p>
                        <p>Generated graphs: {len(graph_files)}</p>
                    </div>
            """
            
            # Add each graph section
            for graph_type, filepath in graph_files.items():
                if filepath and os.path.exists(filepath):
                    graph_name = graph_type.replace('_', ' ').title()
                    filename = os.path.basename(filepath)
                    
                    html_content += f"""
                    <div class="graph-section">
                        <h3>📈 {graph_name}</h3>
                        <img src="{filename}" alt="{graph_name} for {db_name}">
                    </div>
                    """
            
            html_content += f"""
                    <div class="timestamp">
                        <p>Report generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Save HTML report
            html_filename = f"{self.output_dir}/{db_name}_analysis_report.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_filename
            
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return None
