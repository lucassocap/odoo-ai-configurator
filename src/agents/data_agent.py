"""
Data Agent
Handles data ingestion, analysis, enrichment, and synchronization.
"""
import os
from typing import Any, Dict, List, Optional

from .base import OdooAgent
from .data.adapters import CSVAdapter
from .data.analyzer import DataAnalyzer
from .data.state import StateManager
from .data.enricher import ContentEnricher
from .data.images import ImageHandler
from .data.validator import DataValidator

class DataAgent(OdooAgent):
    """
    Intelligent Data Agent that ingests, analyzes, enriches, and syncs data to Odoo.
    """
    
    KEYWORDS = ['import', 'load', 'ingest', 'data', 'csv', 'products']
    
    def __init__(self, connector):
        super().__init__(connector)
        self.analyzer = DataAnalyzer()
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data operations
        
        Params:
            - source: Path to data source (e.g. 'data/raw/products.csv')
            - type: 'product', 'customer', etc. (default: product)
            - dry_run: If True, only analyze/enrich without saving to Odoo.
        """
        source_path = params.get('source')
        dry_run = params.get('dry_run', False)
        
        if not source_path:
            return {'status': 'error', 'message': 'No source path provided'}
            
        # Resolve path relative to project root if needed
        # Determine Project Path for State Manager
        # We assume the agent runs from repo root
        repo_root = os.getcwd()
        if not os.path.isabs(source_path):
             source_path = os.path.abspath(source_path)
             
        project_path = repo_root
        
        # Try to find 'projects/PROJ_NAME' in the path relative to repo root
        try:
            if source_path.startswith(repo_root):
                rel_path = os.path.relpath(source_path, repo_root)
                parts = rel_path.split(os.sep)
                if parts[0] == "projects" and len(parts) > 1:
                    project_path = os.path.join(repo_root, parts[0], parts[1])
        except Exception as e:
            self.log(f"Error determining project path: {e}", "WARNING")
        
        # 1. Ingestion Phase
        try:
            records = self._ingest_data(source_path)
            self.log(f"Ingested {len(records)} raw records")
        except Exception as e:
            self.log(f"Ingestion failed: {e}", "ERROR")
            return {'status': 'error', 'message': str(e)}
            
        if not records:
             return {'status': 'warning', 'message': 'No records found in source'}

        # 2. Analysis Phase
        self.log("Analyzing data structure...")
        analyzed_records = []
        for record in records:
            metadata = self.analyzer.analyze_record(record)
            full_record = {**record, **metadata}
            analyzed_records.append(full_record)
            
        self.log(f"Analyzed {len(analyzed_records)} records")
        
        # Store analysis context in RAG
        if analyzed_records:
            sample = analyzed_records[0]
            context_msg = f"Analyzed {len(analyzed_records)} records from {source_path}. Schema detected: {list(sample.keys())}"
            self.store_context(
                action="analyze_data",
                params={"source": source_path},
                result=str(sample),
                context=context_msg
            )
            self.log("Analysis context stored in RAG")
        
        # 3. Enrichment Phase
        self.log("Starting Enrichment Phase (with Fault Tolerance)...")
        
        state_manager = StateManager(project_path)
        enricher = ContentEnricher(state_manager)
        
        # Enrich batch
        enriched_records = enricher.enrich_batched(analyzed_records, dry_run=True) # Always force dry_run for API simulation for now
        self.log(f"Enriched {len(enriched_records)} records")

        # 4. Image Handling Phase
        self.log("Handling Images...")
        image_handler = ImageHandler(project_path)
        final_records = []
        
        for record in enriched_records:
            # Try to get image
            code = record.get('original_code', '')
            
            # Use new signature: pass full record for AI Context
            image_result = image_handler.get_image_for_product(code, record)
            
            if image_result.get('image_1920'):
                record['image_1920'] = image_result['image_1920']
                record['image_status'] = image_result['image_status']
                record['image_path'] = image_result.get('image_path')
            else:
                record['image_status'] = 'missing'
                
            final_records.append(record)
            
        # 5. Validation Phase
        self.log("Running Data Validation...")
        validator = DataValidator()
        passed, report = validator.validate_batch(final_records)
        
        # Save Validation Report
        report_path = os.path.join(project_path, "data", "validation_report.md")
        try:
            with open(report_path, 'w') as f:
                f.write(report)
            self.log(f"Validation Report generated at: {report_path}")
        except Exception as e:
            self.log(f"Failed to write report: {e}", "WARNING")
            
        self.log(f"Validation Result: {'PASSED' if passed else 'WARNING'}")
        
        # Store execution result in RAG
        final_context = f"Data Enrichment Pipeline Completed. Processed: {len(final_records)}. Validation Status: {'PASSED' if passed else 'WARNING'}. Report: {report_path}"
        self.store_context(
            action="enrich_data",
            params={"source": source_path, "dry_run": dry_run},
            result=f"Processed {len(final_records)} records",
            context=final_context
        )
        self.log("Pipeline result stored in RAG")
        
        # 6. Sync Phase
        if dry_run:
            self.log("Dry run: Skipping synchronization")
            return {
                'status': 'success' if passed else 'warning',
                'records_processed': len(final_records),
                'validation_report': report,
                'sample': final_records[:1] if final_records else []
            }
            
        self.log("Starting Odoo Synchronization...")
        sync_stats = self._sync_to_odoo(final_records)
        self.log(f"Sync Complete: {sync_stats}")
        
        return {
            'status': 'success',
            'message': f"Synced {len(final_records)} records to Odoo",
            'sync_stats': sync_stats,
            'count': len(final_records)
        }

    def _sync_to_odoo(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Push records to Odoo (Create or Update).
        """
        created = 0
        updated = 0
        errors = 0
        
        for record in records:
            try:
                # 1. Prepare Payload
                # Map internal keys to Odoo fields
                vals = {
                    'name': record.get('marketing_title') or record.get('original_code'),
                    'default_code': record.get('original_code'),
                    'description_sale': record.get('marketing_description'),
                    'list_price': record.get('list_price', 0.0), # Sale Price
                    'standard_price': record.get('standard_cost', 0.0), # Cost
                    'type': 'product', # Storable product
                    'detailed_type': 'product',
                    'categ_id': 1, # Default Fallback
                }

                # 1.1 Handle Category (Bearings > SubType)
                cat_name = record.get('sub_category') or record.get('type') or 'Bearings'
                # Simple Cache for performance
                if not hasattr(self, '_cat_cache'):
                    self._cat_cache = {}
                
                categ_id = self._cat_cache.get(cat_name)
                if not categ_id:
                    # Find or Create
                    matches = self.odoo.search('product.category', [('name', '=', cat_name)])
                    if matches:
                        categ_id = matches[0]
                    else:
                        categ_id = self.odoo.create('product.category', {'name': cat_name, 'parent_id': 1})
                    self._cat_cache[cat_name] = categ_id

                vals['categ_id'] = categ_id

                # 1.2 Handle Attributes (Brand)
                brand = record.get('brand')
                if brand:
                   if not hasattr(self, '_attr_brand_id'):
                       attrs = self.odoo.search('product.attribute', [('name', '=', 'Brand')])
                       if attrs:
                           self._attr_brand_id = attrs[0]
                       else:
                           self._attr_brand_id = self.odoo.create('product.attribute', {'name': 'Brand', 'create_variant': 'no_variant'})
                   
                   # Find/Create Value
                   brand_val_ids = self.odoo.search('product.attribute.value', [('attribute_id', '=', self._attr_brand_id), ('name', '=', brand)])
                   if brand_val_ids:
                       val_id = brand_val_ids[0]
                   else:
                       val_id = self.odoo.create('product.attribute.value', {'attribute_id': self._attr_brand_id, 'name': brand})
                   
                   # Replace attributes
                   vals['attribute_line_ids'] = [
                       (5, 0, 0), 
                       (0, 0, {
                           'attribute_id': self._attr_brand_id,
                           'value_ids': [(6, 0, [val_id])]
                       })
                   ]

                # Image
                if record.get('image_1920'):
                    vals['image_1920'] = record['image_1920']
                    
                # 2. Search Existing
                domain = [('default_code', '=', vals['default_code'])]
                existing_ids = self.odoo.search('product.template', domain)
                
                if existing_ids:
                    # Update
                    self.odoo.write('product.template', existing_ids, vals)
                    updated += 1
                else:
                    # Create
                    self.odoo.create('product.template', vals)
                    created += 1

                    
            except Exception as e:
                self.log(f"Sync error for {record.get('original_code')}: {e}", "ERROR")
                errors += 1
                
        return {'created': created, 'updated': updated, 'errors': errors}

    def _ingest_data(self, source_path: str) -> List[Dict[str, Any]]:
        """Determine adapter and read data"""
        # Simple extension check for now
        if source_path.lower().endswith('.csv'):
            adapter = CSVAdapter()
            return adapter.read(source_path)
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
