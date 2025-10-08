"""
Supplier Agent - Supplier Intelligence Analyst
Analyzes supplier performance, flags anomalies, and suggests alternatives
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import json
import logging

from .base_agent import BaseAgent, AgentCapability
from ..core.agent_manager import AgentEvent
from ..core.context_manager import ContextType
from ..utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class SupplierAgent(BaseAgent):
    """
    Supplier Agent - Supplier Intelligence Analyst
    
    Capabilities:
    - Calculate performance scores based on historical data
    - Flag anomalies in supplier behavior
    - Suggest alternative suppliers
    - Analyze trends and patterns
    - Monitor quality metrics
    - Track price competitiveness
    """
    
    def __init__(self, agent_id: str = "supplier_agent"):
        capabilities = [
            AgentCapability.CALCULATE,
            AgentCapability.FLAG,
            AgentCapability.SUGGEST,
            AgentCapability.ANALYZE,
            AgentCapability.MONITOR,
            AgentCapability.RECOMMEND
        ]
        
        super().__init__(agent_id, "Supplier", capabilities)
        
        # Supplier-specific configuration
        self.config.update({
            'performance_weight_price': 0.3,
            'performance_weight_delivery': 0.3,
            'performance_weight_quality': 0.4,
            'anomaly_threshold': 2.0,  # Standard deviations
            'trend_window_days': 90,
            'min_data_points': 5
        })
    
    def handle_event(self, event: AgentEvent, data: Dict[str, Any], context_id: str) -> Any:
        """Handle supplier-related events"""
        try:
            self.log_activity(f"Handling event: {event.value}", data)
            
            if event == AgentEvent.SUPPLIER_UPDATED:
                return self._process_supplier_update(data, context_id)
            elif event == AgentEvent.USER_QUERY:
                return self._handle_user_query(data, context_id)
            else:
                logger.warning(f"Unhandled event type: {event}")
                return None
                
        except Exception as e:
            self.handle_error(e, f"handle_event for {event.value}")
            return None
    
    def _process_supplier_update(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Process supplier update and analyze performance"""
        try:
            supplier_id = data.get('supplier_id')
            if not supplier_id:
                raise ValueError("Missing supplier_id")
            
            # Get supplier performance data
            performance_data = self._get_supplier_performance_data(supplier_id)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(performance_data)
            
            # Check for anomalies
            anomalies = self._detect_anomalies(performance_data)
            
            # Analyze trends
            trends = self._analyze_trends(performance_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(performance_data, anomalies, trends)
            
            # Update context
            result = {
                'supplier_id': supplier_id,
                'performance_score': performance_score,
                'anomalies': anomalies,
                'trends': trends,
                'recommendations': recommendations,
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
            self.update_context(context_id, result)
            self.log_activity("Supplier analysis completed", result)
            
            return result
            
        except Exception as e:
            self.handle_error(e, "process_supplier_update")
            return {'error': str(e)}
    
    def _get_supplier_performance_data(self, supplier_id: str) -> Dict[str, Any]:
        """Get supplier performance data from database"""
        try:
            # This would query the database for supplier performance data
            # For now, return mock data
            performance_data = {
                'supplier_id': supplier_id,
                'total_orders': 25,
                'on_time_deliveries': 22,
                'late_deliveries': 3,
                'quality_issues': 1,
                'average_response_time': 24,  # hours
                'price_competitiveness': 0.85,  # 0-1 scale
                'customer_satisfaction': 4.2,  # 1-5 scale
                'recent_quotes': [
                    {'date': '2024-01-15', 'price': 150.00, 'delivery': 7},
                    {'date': '2024-01-20', 'price': 155.00, 'delivery': 5},
                    {'date': '2024-01-25', 'price': 148.00, 'delivery': 10}
                ]
            }
            
            return performance_data
            
        except Exception as e:
            self.handle_error(e, "get_supplier_performance_data")
            return {}
    
    def _calculate_performance_score(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance score"""
        try:
            # Calculate delivery performance
            total_orders = performance_data.get('total_orders', 1)
            on_time_deliveries = performance_data.get('on_time_deliveries', 0)
            delivery_score = (on_time_deliveries / total_orders) * 100
            
            # Calculate quality score
            quality_issues = performance_data.get('quality_issues', 0)
            quality_score = max(0, 100 - (quality_issues / total_orders) * 100)
            
            # Calculate response time score
            avg_response_time = performance_data.get('average_response_time', 48)
            response_score = max(0, 100 - (avg_response_time / 48) * 100)
            
            # Calculate price competitiveness score
            price_score = performance_data.get('price_competitiveness', 0.5) * 100
            
            # Calculate customer satisfaction score
            satisfaction = performance_data.get('customer_satisfaction', 3.0)
            satisfaction_score = (satisfaction / 5.0) * 100
            
            # Weighted overall score
            overall_score = (
                delivery_score * self.config['performance_weight_delivery'] +
                quality_score * self.config['performance_weight_quality'] +
                response_score * 0.1 +
                price_score * self.config['performance_weight_price'] +
                satisfaction_score * 0.1
            )
            
            return {
                'overall_score': round(overall_score, 2),
                'delivery_score': round(delivery_score, 2),
                'quality_score': round(quality_score, 2),
                'response_score': round(response_score, 2),
                'price_score': round(price_score, 2),
                'satisfaction_score': round(satisfaction_score, 2),
                'grade': self._get_performance_grade(overall_score)
            }
            
        except Exception as e:
            self.handle_error(e, "calculate_performance_score")
            return {'overall_score': 0, 'grade': 'F'}
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert performance score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _detect_anomalies(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in supplier performance"""
        anomalies = []
        
        try:
            # Check for price anomalies
            recent_quotes = performance_data.get('recent_quotes', [])
            if len(recent_quotes) >= 3:
                prices = [quote['price'] for quote in recent_quotes]
                avg_price = sum(prices) / len(prices)
                
                for i, price in enumerate(prices):
                    if abs(price - avg_price) > avg_price * 0.2:  # 20% deviation
                        anomalies.append({
                            'type': 'price_anomaly',
                            'description': f'Price deviation of {((price - avg_price) / avg_price) * 100:.1f}%',
                            'value': price,
                            'expected': avg_price,
                            'severity': 'medium'
                        })
            
            # Check for delivery anomalies
            recent_quotes = performance_data.get('recent_quotes', [])
            if len(recent_quotes) >= 3:
                deliveries = [quote['delivery'] for quote in recent_quotes]
                avg_delivery = sum(deliveries) / len(deliveries)
                
                for i, delivery in enumerate(deliveries):
                    if abs(delivery - avg_delivery) > avg_delivery * 0.5:  # 50% deviation
                        anomalies.append({
                            'type': 'delivery_anomaly',
                            'description': f'Delivery time deviation of {((delivery - avg_delivery) / avg_delivery) * 100:.1f}%',
                            'value': delivery,
                            'expected': avg_delivery,
                            'severity': 'high'
                        })
            
            # Check for quality issues
            quality_issues = performance_data.get('quality_issues', 0)
            total_orders = performance_data.get('total_orders', 1)
            quality_rate = quality_issues / total_orders
            
            if quality_rate > 0.1:  # More than 10% quality issues
                anomalies.append({
                    'type': 'quality_anomaly',
                    'description': f'High quality issue rate: {quality_rate * 100:.1f}%',
                    'value': quality_rate,
                    'expected': 0.05,  # 5% expected
                    'severity': 'high'
                })
            
            return anomalies
            
        except Exception as e:
            self.handle_error(e, "detect_anomalies")
            return []
    
    def _analyze_trends(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in supplier performance"""
        try:
            recent_quotes = performance_data.get('recent_quotes', [])
            if len(recent_quotes) < 3:
                return {'message': 'Insufficient data for trend analysis'}
            
            # Analyze price trends
            prices = [quote['price'] for quote in recent_quotes]
            price_trend = self._calculate_trend(prices)
            
            # Analyze delivery trends
            deliveries = [quote['delivery'] for quote in recent_quotes]
            delivery_trend = self._calculate_trend(deliveries)
            
            # Analyze overall performance trend
            performance_trend = self._analyze_performance_trend(performance_data)
            
            return {
                'price_trend': price_trend,
                'delivery_trend': delivery_trend,
                'performance_trend': performance_trend,
                'analysis_period': f'{len(recent_quotes)} recent quotes',
                'trend_direction': self._get_trend_direction(price_trend, delivery_trend)
            }
            
        except Exception as e:
            self.handle_error(e, "analyze_trends")
            return {'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend for a series of values"""
        try:
            if len(values) < 2:
                return {'direction': 'stable', 'slope': 0, 'confidence': 0}
            
            # Simple linear trend calculation
            n = len(values)
            x = list(range(n))
            y = values
            
            # Calculate slope
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            # Determine direction
            if slope > 0.1:
                direction = 'increasing'
            elif slope < -0.1:
                direction = 'decreasing'
            else:
                direction = 'stable'
            
            # Calculate confidence (simplified)
            confidence = min(1.0, abs(slope) * 10)
            
            return {
                'direction': direction,
                'slope': round(slope, 3),
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            self.handle_error(e, "calculate_trend")
            return {'direction': 'unknown', 'slope': 0, 'confidence': 0}
    
    def _analyze_performance_trend(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall performance trend"""
        try:
            # This would analyze historical performance data
            # For now, return a mock trend analysis
            return {
                'direction': 'improving',
                'slope': 0.05,
                'confidence': 0.8,
                'description': 'Performance has been improving over the last 3 months'
            }
            
        except Exception as e:
            self.handle_error(e, "analyze_performance_trend")
            return {'direction': 'unknown', 'slope': 0, 'confidence': 0}
    
    def _get_trend_direction(self, price_trend: Dict[str, Any], delivery_trend: Dict[str, Any]) -> str:
        """Get overall trend direction"""
        try:
            price_direction = price_trend.get('direction', 'stable')
            delivery_direction = delivery_trend.get('direction', 'stable')
        
            if price_direction == 'decreasing' and delivery_direction == 'decreasing':
                return 'excellent'  # Better prices and faster delivery
            elif price_direction == 'decreasing' and delivery_direction == 'stable':
                return 'good'  # Better prices, stable delivery
            elif price_direction == 'stable' and delivery_direction == 'decreasing':
                return 'good'  # Stable prices, faster delivery
            elif price_direction == 'increasing' and delivery_direction == 'increasing':
                return 'concerning'  # Higher prices and slower delivery
            else:
                return 'mixed'
                
        except Exception as e:
            self.handle_error(e, "get_trend_direction")
            return 'unknown'
    
    def _generate_recommendations(self, performance_data: Dict[str, Any], 
                                 anomalies: List[Dict[str, Any]], trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        try:
            # Performance-based recommendations
            performance_score = self._calculate_performance_score(performance_data)
            overall_score = performance_score.get('overall_score', 0)
            
            if overall_score < 70:
                recommendations.append({
                    'type': 'performance_improvement',
                    'priority': 'high',
                    'description': 'Supplier performance is below acceptable levels',
                    'action': 'Schedule performance review meeting',
                    'timeline': '1 week'
                })
            
            # Anomaly-based recommendations
            for anomaly in anomalies:
                if anomaly['severity'] == 'high':
                    recommendations.append({
                        'type': 'anomaly_investigation',
                        'priority': 'high',
                        'description': f"High severity anomaly detected: {anomaly['description']}",
                        'action': 'Investigate root cause and implement corrective measures',
                        'timeline': '3 days'
                    })
                elif anomaly['severity'] == 'medium':
                    recommendations.append({
                        'type': 'anomaly_monitoring',
                        'priority': 'medium',
                        'description': f"Medium severity anomaly detected: {anomaly['description']}",
                        'action': 'Monitor closely and document patterns',
                        'timeline': '1 week'
                    })
            
            # Trend-based recommendations
            trend_direction = trends.get('trend_direction', 'unknown')
            if trend_direction == 'concerning':
                recommendations.append({
                    'type': 'trend_intervention',
                    'priority': 'medium',
                    'description': 'Concerning trends detected in supplier performance',
                    'action': 'Develop improvement plan with supplier',
                    'timeline': '2 weeks'
                })
            elif trend_direction == 'excellent':
                recommendations.append({
                    'type': 'trend_recognition',
                    'priority': 'low',
                    'description': 'Excellent performance trends detected',
                    'action': 'Consider increasing order volume or expanding relationship',
                    'timeline': '1 month'
                })
            
            # Alternative supplier recommendations
            if overall_score < 60:
                recommendations.append({
                    'type': 'alternative_suppliers',
                    'priority': 'high',
                    'description': 'Consider alternative suppliers due to poor performance',
                    'action': 'Research and evaluate alternative suppliers',
                    'timeline': '2 weeks'
                })
            
            return recommendations
            
        except Exception as e:
            self.handle_error(e, "generate_recommendations")
            return []
    
    def _handle_user_query(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Handle natural language queries about suppliers"""
        try:
            query = data.get('query', '')
            
            # Use AI to understand and respond to the query
            ai_prompt = f"""
            User query about suppliers: {query}
            
            Based on the current supplier context, provide a helpful response.
            Consider:
            - Supplier performance scores
            - Anomalies and issues
            - Trends and patterns
            - Recommendations
            - Alternative suppliers
            
            Be specific and actionable.
            """
            
            response = self.ai_client.generate_response(ai_prompt)
            
            return {
                'query': query,
                'response': response,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.handle_error(e, "handle_user_query")
            return {'error': str(e)}
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    def can_handle_event(self, event: AgentEvent) -> bool:
        """Check if agent can handle a specific event"""
        supplier_events = [
            AgentEvent.SUPPLIER_UPDATED,
            AgentEvent.USER_QUERY
        ]
        return event in supplier_events








