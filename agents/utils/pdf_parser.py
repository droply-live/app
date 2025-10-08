"""
PDF Parser for Agentic Core
Parses PDF documents to extract quote responses and other procurement data
"""

from typing import Dict, List, Any, Optional
import re
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PDFParser:
    """
    PDF Parser for procurement document extraction
    Parses PDF documents to extract quotes, specifications, and other relevant information
    """
    
    def __init__(self):
        self.quote_patterns = [
            r'price[:\s]*\$?([\d,]+\.?\d*)',
            r'cost[:\s]*\$?([\d,]+\.?\d*)',
            r'quote[:\s]*\$?([\d,]+\.?\d*)',
            r'amount[:\s]*\$?([\d,]+\.?\d*)',
            r'total[:\s]*\$?([\d,]+\.?\d*)'
        ]
        
        self.table_patterns = [
            r'item\s*#?\s*([A-Z0-9-]+)',
            r'part\s*#?\s*([A-Z0-9-]+)',
            r'sku\s*#?\s*([A-Z0-9-]+)'
        ]
    
    def parse_quote_response(self, pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a quote response PDF"""
        try:
            content = pdf_data.get('content', '')
            filename = pdf_data.get('filename', '')
            supplier = pdf_data.get('supplier', '')
            
            # Extract key information
            extracted_data = {
                'supplier': supplier,
                'filename': filename,
                'raw_content': content,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract prices
            prices = self._extract_prices(content)
            if prices:
                extracted_data['prices'] = prices
            
            # Extract delivery information
            delivery_info = self._extract_delivery_info(content)
            if delivery_info:
                extracted_data['delivery'] = delivery_info
            
            # Extract part information
            parts = self._extract_part_information(content)
            if parts:
                extracted_data['parts'] = parts
            
            # Extract terms and conditions
            terms = self._extract_terms(content)
            if terms:
                extracted_data['terms'] = terms
            
            # Extract table data
            tables = self._extract_tables(content)
            if tables:
                extracted_data['tables'] = tables
            
            # Determine quote status
            status = self._determine_quote_status(content)
            extracted_data['status'] = status
            
            logger.info(f"Parsed quote response PDF from {supplier}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing quote response PDF: {e}")
            return {'error': str(e)}
    
    def _extract_prices(self, content: str) -> List[Dict[str, Any]]:
        """Extract price information from PDF content"""
        prices = []
        
        try:
            for pattern in self.quote_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    price_value = match.group(1).replace(',', '')
                    try:
                        price_float = float(price_value)
                        prices.append({
                            'value': price_float,
                            'currency': 'USD',  # Default, could be extracted
                            'context': match.group(0),
                            'position': match.start()
                        })
                    except ValueError:
                        continue
            
            # Remove duplicates and sort
            unique_prices = []
            seen_values = set()
            for price in sorted(prices, key=lambda x: x['value']):
                if price['value'] not in seen_values:
                    unique_prices.append(price)
                    seen_values.add(price['value'])
            
            return unique_prices
            
        except Exception as e:
            logger.error(f"Error extracting prices from PDF: {e}")
            return []
    
    def _extract_delivery_info(self, content: str) -> Dict[str, Any]:
        """Extract delivery information from PDF content"""
        delivery_info = {}
        
        try:
            # Delivery patterns
            delivery_patterns = [
                r'delivery[:\s]*(\d+)\s*(days?|weeks?|months?)',
                r'lead\s*time[:\s]*(\d+)\s*(days?|weeks?|months?)',
                r'ship[:\s]*(\d+)\s*(days?|weeks?|months?)',
                r'ready[:\s]*(\d+)\s*(days?|weeks?|months?)'
            ]
            
            for pattern in delivery_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    quantity = int(match.group(1))
                    unit = match.group(2).lower()
                    
                    # Convert to days
                    if unit.startswith('day'):
                        days = quantity
                    elif unit.startswith('week'):
                        days = quantity * 7
                    elif unit.startswith('month'):
                        days = quantity * 30
                    else:
                        days = quantity
                    
                    delivery_info = {
                        'quantity': quantity,
                        'unit': unit,
                        'days': days,
                        'context': match.group(0)
                    }
                    break  # Take first match
            
            return delivery_info
            
        except Exception as e:
            logger.error(f"Error extracting delivery info from PDF: {e}")
            return {}
    
    def _extract_part_information(self, content: str) -> List[Dict[str, Any]]:
        """Extract part information from PDF content"""
        parts = []
        
        try:
            # Part number patterns
            part_patterns = [
                r'part\s*#?\s*([A-Z0-9-]+)',
                r'item\s*#?\s*([A-Z0-9-]+)',
                r'sku\s*#?\s*([A-Z0-9-]+)',
                r'model\s*#?\s*([A-Z0-9-]+)',
                r'p\/n\s*([A-Z0-9-]+)'
            ]
            
            for pattern in part_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    part_num = match.group(1).strip()
                    
                    # Try to extract associated information
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(content), match.end() + 50)
                    context = content[context_start:context_end]
                    
                    part_info = {
                        'part_number': part_num,
                        'context': context,
                        'position': match.start()
                    }
                    
                    # Try to extract quantity and price from context
                    quantity_match = re.search(r'qty[:\s]*(\d+)', context, re.IGNORECASE)
                    if quantity_match:
                        part_info['quantity'] = int(quantity_match.group(1))
                    
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', context)
                    if price_match:
                        try:
                            part_info['price'] = float(price_match.group(1).replace(',', ''))
                        except ValueError:
                            pass
                    
                    parts.append(part_info)
            
            return parts
            
        except Exception as e:
            logger.error(f"Error extracting part information from PDF: {e}")
            return []
    
    def _extract_terms(self, content: str) -> Dict[str, Any]:
        """Extract terms and conditions from PDF content"""
        terms = {}
        
        try:
            # Payment terms
            payment_patterns = [
                r'net\s*(\d+)',
                r'payment\s*terms[:\s]*(\d+)\s*days?',
                r'due\s*in\s*(\d+)\s*days?'
            ]
            
            for pattern in payment_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    terms['payment_days'] = int(match.group(1))
                    break
            
            # Shipping terms
            shipping_patterns = [
                r'fob\s*([a-z\s]+)',
                r'ship\s*from\s*([a-z\s]+)',
                r'delivery\s*to\s*([a-z\s]+)'
            ]
            
            for pattern in shipping_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    terms['shipping_location'] = match.group(1).strip()
                    break
            
            # Warranty terms
            warranty_patterns = [
                r'warranty[:\s]*(\d+)\s*(years?|months?)',
                r'guarantee[:\s]*(\d+)\s*(years?|months?)'
            ]
            
            for pattern in warranty_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    terms['warranty_period'] = match.group(1)
                    terms['warranty_unit'] = match.group(2)
                    break
            
            return terms
            
        except Exception as e:
            logger.error(f"Error extracting terms from PDF: {e}")
            return {}
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract table data from PDF content"""
        tables = []
        
        try:
            # Look for table-like structures
            lines = content.split('\n')
            current_table = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line looks like table data
                if self._is_table_row(line):
                    current_table.append(line)
                else:
                    if current_table:
                        # Process completed table
                        table_data = self._process_table(current_table)
                        if table_data:
                            tables.append(table_data)
                        current_table = []
            
            # Process final table if exists
            if current_table:
                table_data = self._process_table(current_table)
                if table_data:
                    tables.append(table_data)
            
            return tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")
            return []
    
    def _is_table_row(self, line: str) -> bool:
        """Check if a line looks like table data"""
        # Simple heuristic: lines with multiple columns separated by spaces or tabs
        if len(line.split()) >= 3:
            return True
        
        # Check for common table patterns
        table_patterns = [
            r'\d+\s+\d+\s+\d+',  # Numbers separated by spaces
            r'[A-Z0-9-]+\s+[A-Z0-9-]+\s+[A-Z0-9-]+',  # Alphanumeric codes
            r'\$\d+\.\d+\s+\$\d+\.\d+',  # Multiple prices
        ]
        
        for pattern in table_patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _process_table(self, table_lines: List[str]) -> Dict[str, Any]:
        """Process a table into structured data"""
        try:
            if not table_lines:
                return {}
            
            # Split each line into columns
            rows = []
            for line in table_lines:
                columns = line.split()
                if columns:
                    rows.append(columns)
            
            if not rows:
                return {}
            
            # Determine if first row is header
            header = None
            data_rows = rows
            
            # Simple heuristic: if first row contains non-numeric data, it's likely a header
            if rows and not any(re.search(r'\d+', col) for col in rows[0]):
                header = rows[0]
                data_rows = rows[1:]
            
            table_data = {
                'header': header,
                'rows': data_rows,
                'row_count': len(data_rows),
                'column_count': len(data_rows[0]) if data_rows else 0
            }
            
            return table_data
            
        except Exception as e:
            logger.error(f"Error processing table: {e}")
            return {}
    
    def _determine_quote_status(self, content: str) -> str:
        """Determine the status of the quote based on content"""
        try:
            content_lower = content.lower()
            
            # Check for positive indicators
            positive_indicators = [
                'quote', 'pricing', 'price', 'cost', 'estimate',
                'proposal', 'offer', 'bid', 'tender'
            ]
            
            # Check for negative indicators
            negative_indicators = [
                'no quote', 'cannot quote', 'unable to quote',
                'not available', 'out of stock', 'discontinued'
            ]
            
            # Count indicators
            positive_count = sum(1 for indicator in positive_indicators if indicator in content_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in content_lower)
            
            # Determine status
            if negative_count > 0:
                return 'no_quote'
            elif positive_count > 0:
                return 'quote_received'
            else:
                return 'unknown'
                
        except Exception as e:
            logger.error(f"Error determining quote status: {e}")
            return 'unknown'
    
    def parse_specification_document(self, pdf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a specification document PDF"""
        try:
            content = pdf_data.get('content', '')
            filename = pdf_data.get('filename', '')
            
            # Extract specification information
            spec_data = {
                'filename': filename,
                'raw_content': content,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract specifications
            specifications = self._extract_specifications(content)
            if specifications:
                spec_data['specifications'] = specifications
            
            # Extract dimensions
            dimensions = self._extract_dimensions(content)
            if dimensions:
                spec_data['dimensions'] = dimensions
            
            # Extract materials
            materials = self._extract_materials(content)
            if materials:
                spec_data['materials'] = materials
            
            # Extract tolerances
            tolerances = self._extract_tolerances(content)
            if tolerances:
                spec_data['tolerances'] = tolerances
            
            logger.info(f"Parsed specification document: {filename}")
            return spec_data
            
        except Exception as e:
            logger.error(f"Error parsing specification document: {e}")
            return {'error': str(e)}
    
    def _extract_specifications(self, content: str) -> List[Dict[str, Any]]:
        """Extract specifications from content"""
        specifications = []
        
        try:
            # Look for specification patterns
            spec_patterns = [
                r'([a-z\s]+)[:\s]*(\d+\.?\d*)\s*([a-z]+)',
                r'([a-z\s]+)[:\s]*(\d+\.?\d*)\s*([a-z]+)',
            ]
            
            for pattern in spec_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    spec_name = match.group(1).strip()
                    spec_value = match.group(2)
                    spec_unit = match.group(3)
                    
                    specifications.append({
                        'name': spec_name,
                        'value': float(spec_value),
                        'unit': spec_unit,
                        'context': match.group(0)
                    })
            
            return specifications
            
        except Exception as e:
            logger.error(f"Error extracting specifications: {e}")
            return []
    
    def _extract_dimensions(self, content: str) -> List[Dict[str, Any]]:
        """Extract dimensions from content"""
        dimensions = []
        
        try:
            # Dimension patterns
            dimension_patterns = [
                r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*([a-z]+)',
                r'length[:\s]*(\d+\.?\d*)\s*([a-z]+)',
                r'width[:\s]*(\d+\.?\d*)\s*([a-z]+)',
                r'height[:\s]*(\d+\.?\d*)\s*([a-z]+)',
                r'diameter[:\s]*(\d+\.?\d*)\s*([a-z]+)'
            ]
            
            for pattern in dimension_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        dimensions.append({
                            'value': float(match.group(1)),
                            'unit': match.group(2),
                            'context': match.group(0)
                        })
            
            return dimensions
            
        except Exception as e:
            logger.error(f"Error extracting dimensions: {e}")
            return []
    
    def _extract_materials(self, content: str) -> List[str]:
        """Extract materials from content"""
        materials = []
        
        try:
            # Common material patterns
            material_patterns = [
                r'steel',
                r'aluminum',
                r'plastic',
                r'rubber',
                r'copper',
                r'brass',
                r'stainless\s*steel',
                r'carbon\s*steel'
            ]
            
            for pattern in material_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    material = match.group(0).strip()
                    if material not in materials:
                        materials.append(material)
            
            return materials
            
        except Exception as e:
            logger.error(f"Error extracting materials: {e}")
            return []
    
    def _extract_tolerances(self, content: str) -> List[Dict[str, Any]]:
        """Extract tolerances from content"""
        tolerances = []
        
        try:
            # Tolerance patterns
            tolerance_patterns = [
                r'±\s*(\d+\.?\d*)\s*([a-z]+)',
                r'±\s*(\d+\.?\d*)%',
                r'tolerance[:\s]*±\s*(\d+\.?\d*)\s*([a-z]+)'
            ]
            
            for pattern in tolerance_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    tolerance_value = float(match.group(1))
                    tolerance_unit = match.group(2) if len(match.groups()) > 1 else 'units'
                    
                    tolerances.append({
                        'value': tolerance_value,
                        'unit': tolerance_unit,
                        'context': match.group(0)
                    })
            
            return tolerances
            
        except Exception as e:
            logger.error(f"Error extracting tolerances: {e}")
            return []







