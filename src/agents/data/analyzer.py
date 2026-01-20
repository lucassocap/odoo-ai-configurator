"""
Data Analyzer
Extracts structured metadata from raw product codes.
Currently specialized for Bearings nomenclature.
"""
import re
from typing import Any, Dict, Optional

class DataAnalyzer:
    """
    Analyzes raw product data to extract technical specifications.
    """
    
    # Bearing Types Map
    TYPE_MAP = {
        '6': 'Deep Groove Ball Bearing',
        '7': 'Angular Contact Ball Bearing',
        'NU': 'Cylindrical Roller Bearing',
        'NJ': 'Cylindrical Roller Bearing',
        'Nup': 'Cylindrical Roller Bearing',
        'N': 'Cylindrical Roller Bearing',
        '2': 'Spherical Roller Bearing', # e.g., 22212, 23034
        'K': 'Needle Roller Bearing',
        'Q': 'Four Point Contact Ball Bearing',
        '3': 'Tapered Roller Bearing', # Some series start with 3
        '29': 'Spherical Roller Thrust Bearing',
        '5': 'Thrust Ball Bearing',
        'DAC': 'Wheel Bearing (Auto)',
        '4': 'Double Row Deep Groove Ball Bearing', # Series 42xx, 43xx
        '30': 'Tapered Roller Bearing',
        '31': 'Tapered Roller Bearing',
        '32': 'Tapered Roller Bearing',
        '33': 'Tapered Roller Bearing',
    }
    
    def analyze_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single record and return structured metadata.
        """
        item_code = record.get('item_code', '').strip()
        brand = record.get('brand', 'Unknown')
        
        if not item_code:
            return {'error': 'No item code found'}
            
        metadata = {
            'original_code': item_code,
            'category': 'Bearing', # Default based on project context
            'brand': brand,
            'attributes': {},
            # Map CSV financial fields to Odoo
            'standard_cost': self._parse_price(record.get('unit_cost')),  # For Odoo standard_price
            'list_price': self._parse_price(record.get('unit_sale_price')), # For Odoo list_price
            'cost_total': self._parse_price(record.get('cost_total')),
            'sale_total': self._parse_price(record.get('sale_total')),
        }
        
        # Safe extraction
        try:
            specs = self._parse_bearing_code(item_code, brand)
            metadata.update(specs)
            
            # Enrich attributes for Odoo
            if 'type' in specs:
                metadata['attributes']['Bearing Type'] = specs['type']
            if 'bore_mm' in specs:
                metadata['attributes']['Inside Diameter (mm)'] = str(specs['bore_mm'])
            if 'clearance' in specs:
                 metadata['attributes']['Clearance'] = specs['clearance']
                 
        except Exception as e:
            metadata['analysis_error'] = str(e)
            
        return metadata
    
        return metadata
    
    def _parse_bearing_code(self, code: str, brand: str = "") -> Dict[str, Any]:
        """
        Parse standard bearing nomenclature.
        Includes heuristics for non-bearing items like Seals (CR).
        """
        specs = {}
        
        # 0. Brand Specific Overrides
        # CR (Chicago Rawhide) is famous for Seals, not typically standard ISO bearings with these codes
        if brand.upper() in ['CR', 'SKF CR'] and not any(x in code for x in ['60', '62', '63', '22']):
             specs['type'] = 'Oil Seal / Retenedor'
             specs['category'] = 'Seals'
             return specs
        
        # Normalize
        specs = {}
        
        # Normalize
        code_clean = code.replace('/', ' ').replace('-', ' ').upper()
        parts = code_clean.split()
        base_part = parts[0]
        
        # 1. Determine Type based on prefix
        # Spherical often starts with 2 (e.g. 222, 230) and has 5 digits usually
        # Deep groove starts with 6 (e.g. 6204)
        
        prefix = base_part[0]
        if base_part.startswith('NU') or base_part.startswith('NJ'):
            prefix = base_part[:2]
            
        specs['type'] = self.TYPE_MAP.get(prefix, 'Unknown Bearing')
        
        # 2. Extract technical specs from base number
        # Logic for standardized rolling bearings
        # Last 2 digits * 5 = Bore size in mm (for bores >= 20mm and <= 480mm usually)
        
        match = re.search(r'(\d{2})$', base_part)
        if match:
            bore_code = int(match.group(1))
            # Standard rule: multiply by 5
            if 4 <= bore_code <= 99:
                specs['bore_mm'] = bore_code * 5
                
        # 3. Detect Features (Suffixes)
        suffix_text = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        # Clearance
        if 'C3' in code_clean:
            specs['clearance'] = 'C3 (Greater than normal)'
        elif 'C4' in code_clean:
             specs['clearance'] = 'C4 (Greater than C3)'
        elif 'C2' in code_clean:
             specs['clearance'] = 'C2 (Less than normal)'
        else:
             specs['clearance'] = 'CN (Normal)'
             
        # Tapered Bore
        if 'K' in code_clean.split(): # Isolated K usually means tapered
            specs['bore_type'] = 'Tapered (1:12)'
        elif 'K30' in code_clean:
            specs['bore_type'] = 'Tapered (1:30)'
        else:
            specs['bore_type'] = 'Cylindrical'
            
        # Cage/Design
        if 'W33' in code_clean:
            specs['features'] = 'Lubrication groove and holes in outer ring'
            
        specs['series'] = base_part[:-2] # Rough series extraction
        
        return specs

    def _parse_price(self, value: Any) -> float:
        """Clean and convert price strings to float"""
        if not value:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        try:
            # Remove currency symbols and thousands separators
            clean = str(value).replace('$', '').replace(',', '').strip()
            return float(clean)
        except ValueError:
            return 0.0
