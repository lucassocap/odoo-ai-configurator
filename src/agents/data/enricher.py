"""
Content Enricher
Generates marketing content from technical metadata using AI.
"""
import os
import time
import sys
from typing import Any, Dict

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .state import StateManager

class ContentEnricher:
    """
    Enriches product data with marketing descriptions using OpenAI.
    """
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        
        # Initialize OpenAI Client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Try loading from .env manually if not in env vars
            try:
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.getenv("OPENAI_API_KEY")
            except:
                pass
                
        if OpenAI and api_key:
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI Client Initialized")
        else:
            self.client = None
            print("⚠️ OpenAI API Key not found or library missing. Using mock generation.")

    def enrich_batched(self, records: list[Dict[str, Any]], dry_run: bool = False) -> list[Dict[str, Any]]:
        """
        Enrich a list of records.
        """
        enriched_results = []
        total = len(records)
        
        print(f"\n🚀 Starting AI Enrichment for {total} records...")
        
        for idx, record in enumerate(records, 1):
            # Identifier
            record_id = record.get('original_code') or record.get('item_code')
            
            # Progress Log
            sys.stdout.write(f"\r⏳ Processing {idx}/{total}: {record_id:<20}")
            sys.stdout.flush()
            
            if not record_id:
                continue 
                
            # Check state
            if self.state_manager.is_processed(record_id):
                existing_data = self.state_manager.get_processed_data(record_id)
                enriched_results.append({**record, **existing_data})
                continue
                
            # Generate new content
            try:
                # Force real generation if client exists, even if 'dry_run' was passed to data agent 
                # (We treat dry_run in DataAgent as "Don't sync to Odoo", but we DO want to generate text now)
                generated_content = self._generate_content(record)
                
                # Checkpoint immediately
                self.state_manager.mark_processed(record_id, generated_content)
                
                enriched_results.append({**record, **generated_content})
                
            except Exception as e:
                print(f"\n❌ Error on {record_id}: {e}")
                enriched_results.append({**record, 'enrichment_error': str(e)})
                
        print(f"\n✅ Enrichment Complete. {len(enriched_results)} records ready.")
        return enriched_results
    
    def _generate_content(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content using OpenAI
        """
        brand = record.get('brand', 'Generic')
        specs = record.get('attributes', {})
        specs_str = ", ".join([f"{k}: {v}" for k, v in specs.items()])
        model = record.get('original_code')
        
        # If no client, fallback to mock
        if not self.client:
            return self._mock_generation(record, brand, specs)
            
        prompt = f"""
        You are an expert industrial copywriter for {brand}.
        Write a premium product description for a bearing/component.
        
        Product: {model}
        Type: {record.get('type')}
        Specs: {specs_str}
        
        Output valid JSON only:
        {{
            "marketing_title": "SEO Title including Brand & Series (e.g. SKF 23034...)",
            "marketing_description": "2 paragraphs highlighting stats. Mention Brand '{brand}' explicitly.",
            "meta_keywords": "brand, code, type, specific_feature",
            "features_list": "Bullet 1 | Bullet 2 | Bullet 3",
            "taxonomy": {{
                "main_category": "Bearings",
                "sub_category": "{record.get('type')}",
                "brand": "{brand}"
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125", # Cost effective and fast
                messages=[
                    {"role": "system", "content": "You are a helpful industrial assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={ "type": "json_object" } 
            )
            
            content = response.choices[0].message.content
            import json
            data = json.loads(content)
            data['enrichment_source'] = 'openai_gpt35'
            return data
            
        except Exception as e:
            print(f" OpenAI API Error: {e}")
            return self._mock_generation(record, brand, specs)

    def _mock_generation(self, record, brand, specs) -> Dict[str, Any]:
        """Mock output for fallback"""
        # ... (same as before)
        code = record.get('original_code', 'Unknown')
        b_type = record.get('type', 'Industrial Component')
        
        return {
            'marketing_title': f"{brand} {code} - Premium {b_type}",
            'marketing_description': f"Upgrade your machinery with the {brand} {code}. High-performance {b_type}.",
            'meta_keywords': f"{brand}, {code}, {b_type}",
            'enrichment_source': 'simulated_ai'
        }
