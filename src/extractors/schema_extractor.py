import sqlalchemy as sa
from sqlalchemy import inspect, text
import pymongo
import json
from typing import Dict, List, Any, Optional
import logging

class MultiDBSchemaExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_dbs = ['postgresql', 'mysql', 'sqlite', 'oracle', 'mssql']
    
    def extract_relational_schema(self, connection_string: str) -> Dict[str, Any]:
        """Extract schema from relational databases"""
        try:
            engine = sa.create_engine(connection_string)
            inspector = inspect(engine)
            
            schema_data = {
                'database_type': engine.dialect.name,
                'connection_info': {
                    'dialect': engine.dialect.name,
                    'driver': engine.dialect.driver
                },
                'tables': {},
                'views': [],
                'indexes': {},
                'constraints': {}
            }
            
            # Extract table information
            table_names = inspector.get_table_names()
            self.logger.info(f"Found {len(table_names)} tables")
            
            for table_name in table_names:
                self.logger.info(f"Processing table: {table_name}")
                
                # Get table details
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                primary_keys = inspector.get_pk_constraint(table_name)
                indexes = inspector.get_indexes(table_name)
                check_constraints = inspector.get_check_constraints(table_name)
                unique_constraints = inspector.get_unique_constraints(table_name)
                
                # Get row count (safely)
                row_count = self._get_row_count_safe(engine, table_name)
                
                # Analyze column patterns
                column_analysis = self._analyze_columns(columns)
                
                schema_data['tables'][table_name] = {
                    'columns': columns,
                    'primary_keys': primary_keys,
                    'foreign_keys': foreign_keys,
                    'indexes': indexes,
                    'check_constraints': check_constraints,
                    'unique_constraints': unique_constraints,
                    'row_count': row_count,
                    'column_analysis': column_analysis
                }
            
            # Extract views
            try:
                view_names = inspector.get_view_names()
                schema_data['views'] = view_names
            except Exception:
                schema_data['views'] = []
            
            return schema_data
            
        except Exception as e:
            self.logger.error(f"Error extracting relational schema: {e}")
            raise
    
    def extract_mongodb_schema(self, connection_string: str, database_name: str) -> Dict[str, Any]:
        """Extract schema from MongoDB"""
        try:
            client = pymongo.MongoClient(connection_string)
            db = client[database_name]
            
            schema_data = {
                'database_type': 'mongodb',
                'database_name': database_name,
                'collections': {},
                'sample_documents': {},
                'indexes': {}
            }
            
            collection_names = db.list_collection_names()
            self.logger.info(f"Found {len(collection_names)} collections")
            
            for collection_name in collection_names:
                self.logger.info(f"Processing collection: {collection_name}")
                
                collection = db[collection_name]
                
                # Get collection stats
                try:
                    stats = db.command("collStats", collection_name)
                except:
                    stats = {'count': 0, 'size': 0, 'avgObjSize': 0}
                
                # Sample documents to infer schema
                sample_docs = list(collection.find().limit(100))
                
                # Infer field structure
                field_analysis = self._analyze_mongo_fields(sample_docs)
                
                # Get indexes
                collection_indexes = list(collection.list_indexes())
                
                schema_data['collections'][collection_name] = {
                    'document_count': stats.get('count', 0),
                    'size_bytes': stats.get('size', 0),
                    'avg_doc_size': stats.get('avgObjSize', 0),
                    'field_analysis': field_analysis,
                    'indexes': collection_indexes
                }
                
                # Store sample documents (first 5)
                schema_data['sample_documents'][collection_name] = sample_docs[:5]
                
            client.close()
            return schema_data
            
        except Exception as e:
            self.logger.error(f"Error extracting MongoDB schema: {e}")
            raise
    
    def _get_row_count_safe(self, engine, table_name: str) -> Optional[int]:
        """Safely get row count for a table"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
        except Exception as e:
            self.logger.warning(f"Could not get row count for {table_name}: {e}")
            return None
    
    def _analyze_columns(self, columns: List[Dict]) -> Dict[str, Any]:
        """Analyze column patterns and characteristics"""
        analysis = {
            'total_columns': len(columns),
            'data_types': {},
            'nullable_columns': 0,
            'potential_pii': [],
            'naming_patterns': []
        }
        
        for col in columns:
            # Count data types
            col_type = str(col['type'])
            analysis['data_types'][col_type] = analysis['data_types'].get(col_type, 0) + 1
            
            # Count nullable columns
            if col.get('nullable', True):
                analysis['nullable_columns'] += 1
            
            # Identify potential PII
            col_name_lower = col['name'].lower()
            pii_patterns = ['email', 'phone', 'ssn', 'social', 'password', 'credit', 'card']
            if any(pattern in col_name_lower for pattern in pii_patterns):
                analysis['potential_pii'].append(col['name'])
        
        return analysis
    
    def _analyze_mongo_fields(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze MongoDB document fields"""
        if not documents:
            return {}
        
        field_types = {}
        field_presence = {}
        
        for doc in documents:
            self._traverse_document(doc, field_types, field_presence, "")
        
        # Calculate field statistics
        total_docs = len(documents)
        field_stats = {}
        
        for field, types in field_types.items():
            field_stats[field] = {
                'types': list(set(types)),
                'presence_percentage': (field_presence[field] / total_docs) * 100,
                'is_required': field_presence[field] == total_docs
            }
        
        return field_stats
    
    def _traverse_document(self, obj, field_types, field_presence, prefix):
        """Recursively traverse MongoDB document structure"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                field_name = f"{prefix}.{key}" if prefix else key
                
                # Track field presence
                field_presence[field_name] = field_presence.get(field_name, 0) + 1
                
                # Track field types
                if field_name not in field_types:
                    field_types[field_name] = []
                
                field_types[field_name].append(type(value).__name__)
                
                # Recurse into nested objects
                if isinstance(value, (dict, list)):
                    self._traverse_document(value, field_types, field_presence, field_name)
        
        elif isinstance(obj, list) and obj:
            # Analyze first item in list
            self._traverse_document(obj[0], field_types, field_presence, prefix)
