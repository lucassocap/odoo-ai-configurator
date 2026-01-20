"""
Data Validator
Checks data integrity and generates validation reports.
"""
from typing import List, Dict, Any, Tuple

class DataValidator:
    """
    Validates enriched data before Odoo sync.
    """
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate a batch of records.
        Returns: (passed, report_text)
        """
        total = len(records)
        passed = 0
        issues = []
        
        # Stats
        with_image = 0
        with_desc = 0
        valid_price = 0
        
        for record in records:
            r_issues = []
            
            # Check Image
            if record.get('image_1920'):
                with_image += 1
            else:
                r_issues.append("Missing Image")
                
            # Check Description
            desc = record.get('marketing_description', '')
            if desc and len(desc) > 20:
                with_desc += 1
            else:
                r_issues.append("Weak/Missing Description")
                
            # Check Price
            try:
                price = float(record.get('unit_sale_price', 0))
                if price > 0:
                    valid_price += 1
                else:
                    r_issues.append("Zero Price")
            except:
                r_issues.append("Invalid Price Format")
                
            if not r_issues:
                passed += 1
            else:
                # Log first 10 bad records
                if len(issues) < 10:
                    code = record.get('original_code', 'Unknown')
                    issues.append(f"- **{code}**: {', '.join(r_issues)}")

        success_rate = (passed / total) * 100 if total > 0 else 0
        
        # Generate Report
        report = f"""
# Data Validation Report

## Summary
- **Total Records**: {total}
- **Ready to Sync**: {passed} ({success_rate:.1f}%)
- **Issues Found**: {total - passed}

## Quality Metrics
- 📸 **Has Image**: {with_image} ({(with_image/total)*100:.1f}%)
- 📝 **Has Description**: {with_desc} ({(with_desc/total)*100:.1f}%)
- 💰 **Valid Price**: {valid_price} ({(valid_price/total)*100:.1f}%)

## Sample Issues
{chr(10).join(issues)}
{f'... and {total - passed - 10} more.' if (total - passed) > 10 else ''}
        """
        
        return (success_rate > 80), report
