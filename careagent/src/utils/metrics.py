#!/usr/bin/env python3
"""
Metrics collection and analysis for the multi-agent platform
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from contextlib import contextmanager

from src.utils.logging import get_logger

logger = get_logger("metrics_collector")

@dataclass
class RoutingMetric:
    """Metrics for a single routing decision"""
    timestamp: datetime
    utterance: str
    predicted_intent: str
    actual_intent: Optional[str]
    confidence_score: float
    response_time: float
    success: bool
    error_message: Optional[str]

@dataclass
class BedrockCallMetric:
    """Metrics for a Bedrock agent call"""
    timestamp: datetime
    agent_type: str
    model_id: str
    input_tokens: int
    output_tokens: int
    response_time: float
    success: bool
    error_message: Optional[str]
    cost_estimate: float

@dataclass
class DiscrepancyMetric:
    """Metrics for discrepancy detection"""
    timestamp: datetime
    scenario_id: str
    discrepancy_type: str
    severity: str
    detected_by: str
    description: str
    resolved: bool

class MetricsCollector:
    """Centralized metrics collection for the multi-agent platform"""
    
    def __init__(self, output_dir: str = "metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.routing_metrics: List[RoutingMetric] = []
        self.bedrock_metrics: List[BedrockCallMetric] = []
        self.discrepancy_metrics: List[DiscrepancyMetric] = []
        
        self.session_start = datetime.now()
        self.total_requests = 0
        self.successful_requests = 0
        
    def record_routing_decision(
        self,
        utterance: str,
        predicted_intent: str,
        actual_intent: Optional[str] = None,
        confidence_score: float = 0.0,
        response_time: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Record a routing decision"""
        metric = RoutingMetric(
            timestamp=datetime.now(),
            utterance=utterance,
            predicted_intent=predicted_intent,
            actual_intent=actual_intent,
            confidence_score=confidence_score,
            response_time=response_time,
            success=success,
            error_message=error_message
        )
        
        self.routing_metrics.append(metric)
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            
        logger.debug(f"Recorded routing decision: {predicted_intent} (success={success})")
    
    def record_bedrock_call(
        self,
        agent_type: str,
        model_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        response_time: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None,
        cost_estimate: float = 0.0
    ):
        """Record a Bedrock agent call"""
        metric = BedrockCallMetric(
            timestamp=datetime.now(),
            agent_type=agent_type,
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time=response_time,
            success=success,
            error_message=error_message,
            cost_estimate=cost_estimate
        )
        
        self.bedrock_metrics.append(metric)
        logger.debug(f"Recorded Bedrock call: {agent_type} (success={success})")
    
    def record_discrepancy(
        self,
        scenario_id: str,
        discrepancy_type: str,
        severity: str,
        detected_by: str,
        description: str,
        resolved: bool = False
    ):
        """Record a detected discrepancy"""
        metric = DiscrepancyMetric(
            timestamp=datetime.now(),
            scenario_id=scenario_id,
            discrepancy_type=discrepancy_type,
            severity=severity,
            detected_by=detected_by,
            description=description,
            resolved=resolved
        )
        
        self.discrepancy_metrics.append(metric)
        logger.info(f"Recorded discrepancy: {discrepancy_type} (severity={severity})")
    
    @contextmanager
    def timed_operation(self, operation_name: str):
        """Context manager for timing operations"""
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            logger.debug(f"{operation_name} took {end_time - start_time:.3f}s")
    
    def get_routing_accuracy(self) -> float:
        """Calculate routing accuracy"""
        if not self.routing_metrics:
            return 0.0
        
        correct_routes = sum(
            1 for m in self.routing_metrics 
            if m.actual_intent and m.predicted_intent == m.actual_intent
        )
        
        total_with_actual = sum(
            1 for m in self.routing_metrics 
            if m.actual_intent is not None
        )
        
        return correct_routes / total_with_actual if total_with_actual > 0 else 0.0
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate"""
        return self.successful_requests / self.total_requests if self.total_requests > 0 else 0.0
    
    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.routing_metrics:
            return 0.0
        
        response_times = [m.response_time for m in self.routing_metrics if m.response_time > 0]
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def get_bedrock_usage_stats(self) -> Dict[str, Any]:
        """Get Bedrock usage statistics"""
        if not self.bedrock_metrics:
            return {}
        
        stats = {
            "total_calls": len(self.bedrock_metrics),
            "successful_calls": sum(1 for m in self.bedrock_metrics if m.success),
            "total_input_tokens": sum(m.input_tokens for m in self.bedrock_metrics),
            "total_output_tokens": sum(m.output_tokens for m in self.bedrock_metrics),
            "total_cost_estimate": sum(m.cost_estimate for m in self.bedrock_metrics),
            "avg_response_time": sum(m.response_time for m in self.bedrock_metrics) / len(self.bedrock_metrics),
            "agent_usage": {}
        }
        
        # Agent usage breakdown
        for metric in self.bedrock_metrics:
            agent = metric.agent_type
            if agent not in stats["agent_usage"]:
                stats["agent_usage"][agent] = {
                    "calls": 0,
                    "successful_calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_estimate": 0.0
                }
            
            stats["agent_usage"][agent]["calls"] += 1
            if metric.success:
                stats["agent_usage"][agent]["successful_calls"] += 1
            stats["agent_usage"][agent]["input_tokens"] += metric.input_tokens
            stats["agent_usage"][agent]["output_tokens"] += metric.output_tokens
            stats["agent_usage"][agent]["cost_estimate"] += metric.cost_estimate
        
        return stats
    
    def get_discrepancy_stats(self) -> Dict[str, Any]:
        """Get discrepancy detection statistics"""
        if not self.discrepancy_metrics:
            return {}
        
        stats = {
            "total_discrepancies": len(self.discrepancy_metrics),
            "resolved_discrepancies": sum(1 for m in self.discrepancy_metrics if m.resolved),
            "by_type": {},
            "by_severity": {},
            "by_detector": {}
        }
        
        for metric in self.discrepancy_metrics:
            # By type
            if metric.discrepancy_type not in stats["by_type"]:
                stats["by_type"][metric.discrepancy_type] = 0
            stats["by_type"][metric.discrepancy_type] += 1
            
            # By severity
            if metric.severity not in stats["by_severity"]:
                stats["by_severity"][metric.severity] = 0
            stats["by_severity"][metric.severity] += 1
            
            # By detector
            if metric.detected_by not in stats["by_detector"]:
                stats["by_detector"][metric.detected_by] = 0
            stats["by_detector"][metric.detected_by] += 1
        
        return stats
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report"""
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        report = {
            "session_info": {
                "start_time": self.session_start.isoformat(),
                "duration_seconds": session_duration,
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "success_rate": self.get_success_rate()
            },
            "routing_metrics": {
                "total_routing_decisions": len(self.routing_metrics),
                "routing_accuracy": self.get_routing_accuracy(),
                "avg_response_time": self.get_avg_response_time(),
                "intent_distribution": self._get_intent_distribution()
            },
            "bedrock_metrics": self.get_bedrock_usage_stats(),
            "discrepancy_metrics": self.get_discrepancy_stats(),
            "performance_indicators": {
                "requests_per_second": self.total_requests / session_duration if session_duration > 0 else 0,
                "avg_tokens_per_request": (
                    self.get_bedrock_usage_stats().get("total_input_tokens", 0) / self.total_requests
                    if self.total_requests > 0 else 0
                )
            }
        }
        
        return report
    
    def _get_intent_distribution(self) -> Dict[str, int]:
        """Get distribution of predicted intents"""
        distribution = {}
        for metric in self.routing_metrics:
            intent = metric.predicted_intent
            distribution[intent] = distribution.get(intent, 0) + 1
        return distribution
    
    def save_detailed_metrics(self, filename_prefix: str = "metrics"):
        """Save detailed metrics to JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save routing metrics
        routing_file = self.output_dir / f"{filename_prefix}_routing_{timestamp}.json"
        with open(routing_file, 'w') as f:
            json.dump([asdict(m) for m in self.routing_metrics], f, indent=2, default=str)
        
        # Save Bedrock metrics
        bedrock_file = self.output_dir / f"{filename_prefix}_bedrock_{timestamp}.json"
        with open(bedrock_file, 'w') as f:
            json.dump([asdict(m) for m in self.bedrock_metrics], f, indent=2, default=str)
        
        # Save discrepancy metrics
        discrepancy_file = self.output_dir / f"{filename_prefix}_discrepancies_{timestamp}.json"
        with open(discrepancy_file, 'w') as f:
            json.dump([asdict(m) for m in self.discrepancy_metrics], f, indent=2, default=str)
        
        # Save summary report
        summary_file = self.output_dir / f"{filename_prefix}_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(self.generate_summary_report(), f, indent=2, default=str)
        
        logger.info(f"Metrics saved to {self.output_dir}")
        
        return {
            "routing_file": str(routing_file),
            "bedrock_file": str(bedrock_file),
            "discrepancy_file": str(discrepancy_file),
            "summary_file": str(summary_file)
        }
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        self.routing_metrics.clear()
        self.bedrock_metrics.clear()
        self.discrepancy_metrics.clear()
        self.total_requests = 0
        self.successful_requests = 0
        self.session_start = datetime.now()
        logger.info("Metrics cleared")

# Global metrics collector instance
global_metrics = MetricsCollector()

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return global_metrics
