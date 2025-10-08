"""
Email Parser for Agentic Core
Parses emails to extract quote responses and other procurement data
"""

from typing import Dict, List, Any, Optional
import re
import json
import logging
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailParser:
    """
    Email Parser for procurement data extraction
    Parses emails to extract quotes, responses, and other relevant information
    """
    
    def __init__(self):
        self.quote_patterns = [
            r'price[:\s]*\$?([\d,]+\.?\d*)',
            r'cost[:\s]*\$?([\d,]+\.?\d*)',
            r'quote[:\s]*\$?([\d,]+\.?\d*)',
            r'amount[:\s]*\$?([\d,]+\.?\d*)',
            r'total[:\s]*\$?([\d,]+\.?\d*)'
        ]
        
        self.delivery_patterns = [
            r'delivery[:\s]*(\d+)\s*(days?|weeks?|months?)',
            r'lead\s*time[:\s]*(\d+)\s*(days?|weeks?|months?)',
            r'ship[:\s]*(\d+)\s*(days?|weeks?|months?)',
            r'ready[:\s]*(\d+)\s*(days?|weeks?|months?)'
        ]
        
        self.date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}'
        ]
    
    def parse_quote_response(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a quote response email"""
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            # Extract key information
            extracted_data = {
                'supplier_email': sender,
                'subject': subject,
                'raw_body': body,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract prices
            prices = self._extract_prices(body)
            if prices:
                extracted_data['prices'] = prices
            
            # Extract delivery information
            delivery_info = self._extract_delivery_info(body)
            if delivery_info:
                extracted_data['delivery'] = delivery_info
            
            # Extract dates
            dates = self._extract_dates(body)
            if dates:
                extracted_data['dates'] = dates
            
            # Extract part numbers
            part_numbers = self._extract_part_numbers(body)
            if part_numbers:
                extracted_data['part_numbers'] = part_numbers
            
            # Extract terms and conditions
            terms = self._extract_terms(body)
            if terms:
                extracted_data['terms'] = terms
            
            # Determine quote status
            status = self._determine_quote_status(body)
            extracted_data['status'] = status
            
            logger.info(f"Parsed quote response from {sender}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing quote response: {e}")
            return {'error': str(e)}
    
    def _extract_prices(self, text: str) -> List[Dict[str, Any]]:
        """Extract price information from text"""
        prices = []
        
        try:
            for pattern in self.quote_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
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
            logger.error(f"Error extracting prices: {e}")
            return []
    
    def _extract_delivery_info(self, text: str) -> Dict[str, Any]:
        """Extract delivery information from text"""
        delivery_info = {}
        
        try:
            for pattern in self.delivery_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
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
            logger.error(f"Error extracting delivery info: {e}")
            return {}
    
    def _extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates from text"""
        dates = []
        
        try:
            for pattern in self.date_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    date_str = match.group(1)
                    try:
                        # Try to parse the date
                        parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
                        dates.append({
                            'date': parsed_date.isoformat(),
                            'raw': date_str,
                            'context': match.group(0)
                        })
                    except ValueError:
                        try:
                            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                            dates.append({
                                'date': parsed_date.isoformat(),
                                'raw': date_str,
                                'context': match.group(0)
                            })
                        except ValueError:
                            continue
            
            return dates
            
        except Exception as e:
            logger.error(f"Error extracting dates: {e}")
            return []
    
    def _extract_part_numbers(self, text: str) -> List[str]:
        """Extract part numbers from text"""
        part_numbers = []
        
        try:
            # Common part number patterns
            patterns = [
                r'part\s*#?\s*([A-Z0-9-]+)',
                r'item\s*#?\s*([A-Z0-9-]+)',
                r'sku\s*#?\s*([A-Z0-9-]+)',
                r'model\s*#?\s*([A-Z0-9-]+)',
                r'p\/n\s*([A-Z0-9-]+)'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    part_num = match.group(1).strip()
                    if part_num not in part_numbers:
                        part_numbers.append(part_num)
            
            return part_numbers
            
        except Exception as e:
            logger.error(f"Error extracting part numbers: {e}")
            return []
    
    def _extract_terms(self, text: str) -> Dict[str, Any]:
        """Extract terms and conditions from text"""
        terms = {}
        
        try:
            # Payment terms
            payment_patterns = [
                r'net\s*(\d+)',
                r'payment\s*terms[:\s]*(\d+)\s*days?',
                r'due\s*in\s*(\d+)\s*days?'
            ]
            
            for pattern in payment_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
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
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    terms['shipping_location'] = match.group(1).strip()
                    break
            
            # Warranty terms
            warranty_patterns = [
                r'warranty[:\s]*(\d+)\s*(years?|months?)',
                r'guarantee[:\s]*(\d+)\s*(years?|months?)'
            ]
            
            for pattern in warranty_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    terms['warranty_period'] = match.group(1)
                    terms['warranty_unit'] = match.group(2)
                    break
            
            return terms
            
        except Exception as e:
            logger.error(f"Error extracting terms: {e}")
            return {}
    
    def _determine_quote_status(self, text: str) -> str:
        """Determine the status of the quote based on text content"""
        try:
            text_lower = text.lower()
            
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
            
            # Check for no response indicators
            no_response_indicators = [
                'no response', 'no reply', 'silence',
                'ignored', 'unanswered'
            ]
            
            # Count indicators
            positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
            negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
            no_response_count = sum(1 for indicator in no_response_indicators if indicator in text_lower)
            
            # Determine status
            if no_response_count > 0:
                return 'no_response'
            elif negative_count > 0:
                return 'no_quote'
            elif positive_count > 0:
                return 'quote_received'
            else:
                return 'unknown'
                
        except Exception as e:
            logger.error(f"Error determining quote status: {e}")
            return 'unknown'
    
    def parse_supplier_confirmation(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse supplier confirmation email"""
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            # Extract confirmation information
            confirmation_data = {
                'supplier_email': sender,
                'subject': subject,
                'raw_body': body,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Check for confirmation keywords
            confirmation_keywords = [
                'confirmed', 'accepted', 'approved', 'acknowledged',
                'received', 'processing', 'in production'
            ]
            
            text_lower = body.lower()
            confirmation_found = any(keyword in text_lower for keyword in confirmation_keywords)
            
            confirmation_data['is_confirmed'] = confirmation_found
            
            # Extract delivery date if mentioned
            delivery_dates = self._extract_dates(body)
            if delivery_dates:
                confirmation_data['delivery_dates'] = delivery_dates
            
            # Extract order reference
            order_ref_patterns = [
                r'order\s*#?\s*([A-Z0-9-]+)',
                r'po\s*#?\s*([A-Z0-9-]+)',
                r'reference\s*#?\s*([A-Z0-9-]+)'
            ]
            
            for pattern in order_ref_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    confirmation_data['order_reference'] = match.group(1)
                    break
            
            logger.info(f"Parsed supplier confirmation from {sender}")
            return confirmation_data
            
        except Exception as e:
            logger.error(f"Error parsing supplier confirmation: {e}")
            return {'error': str(e)}
    
    def parse_delay_notification(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse delay notification email"""
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            # Extract delay information
            delay_data = {
                'supplier_email': sender,
                'subject': subject,
                'raw_body': body,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Check for delay keywords
            delay_keywords = [
                'delay', 'delayed', 'late', 'postponed', 'rescheduled',
                'behind schedule', 'running late', 'extended'
            ]
            
            text_lower = body.lower()
            delay_found = any(keyword in text_lower for keyword in delay_keywords)
            
            delay_data['is_delay'] = delay_found
            
            # Extract new delivery date
            new_dates = self._extract_dates(body)
            if new_dates:
                delay_data['new_delivery_dates'] = new_dates
            
            # Extract delay reason
            reason_patterns = [
                r'delay\s*reason[:\s]*([^.]+)',
                r'because[:\s]*([^.]+)',
                r'due\s*to[:\s]*([^.]+)'
            ]
            
            for pattern in reason_patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    delay_data['delay_reason'] = match.group(1).strip()
                    break
            
            logger.info(f"Parsed delay notification from {sender}")
            return delay_data
            
        except Exception as e:
            logger.error(f"Error parsing delay notification: {e}")
            return {'error': str(e)}








