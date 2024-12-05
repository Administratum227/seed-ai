"""Network metrics and monitoring for SEED agents.

Provides real-time monitoring of network health, performance metrics,
and diagnostic capabilities for the agent network.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Deque
from collections import deque
import statistics
import asyncio

@dataclass
class NetworkMetrics:
    """Container for network performance metrics."""
    
    # Message latency tracking
    latency_window: int = 100
    latency_samples: Deque[float] = field(
        default_factory=lambda: deque(maxlen=100)
    )
    
    # Message delivery tracking
    sent_messages: int = 0
    delivered_messages: int = 0
    failed_messages: int = 0
    
    # Bandwidth usage (bytes)
    bytes_sent: int = 0
    bytes_received: int = 0
    
    def add_latency_sample(self, latency_ms: float) -> None:
        """Add a new latency measurement."""
        self.latency_samples.append(latency_ms)
    
    def get_average_latency(self) -> Optional[float]:
        """Get average message latency in milliseconds."""
        if not self.latency_samples:
            return None
        return statistics.mean(self.latency_samples)
    
    def record_message_sent(self, size_bytes: int) -> None:
        """Record a sent message."""
        self.sent_messages += 1
        self.bytes_sent += size_bytes
    
    def record_message_delivered(self) -> None:
        """Record a successfully delivered message."""
        self.delivered_messages += 1
    
    def record_message_failed(self) -> None:
        """Record a failed message delivery."""
        self.failed_messages += 1
    
    def get_delivery_rate(self) -> float:
        """Calculate message delivery success rate."""
        if self.sent_messages == 0:
            return 1.0
        return self.delivered_messages / self.sent_messages

class NetworkMonitor:
    """Monitors and collects network performance metrics.
    
    Features:
    - Real-time metric collection
    - Performance analysis
    - Health monitoring
    - Alert generation
    """
    
    def __init__(self):
        self.metrics = NetworkMetrics()
        self._started_at = datetime.now()
        self._alert_callbacks = []
    
    async def start_monitoring(self) -> None:
        """Start network monitoring."""
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop()
        )
    
    async def stop_monitoring(self) -> None:
        """Stop network monitoring."""
        if hasattr(self, '_monitoring_task'):
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
    
    def add_alert_callback(self, callback: callable) -> None:
        """Add callback for network alerts."""
        self._alert_callbacks.append(callback)
    
    async def get_network_health(self) -> Dict[str, Any]:
        """Get current network health status.
        
        Returns:
            Dictionary containing:
            - Average message latency
            - Message delivery rate
            - Bandwidth usage
            - Network stability score
        """
        avg_latency = self.metrics.get_average_latency()
        delivery_rate = self.metrics.get_delivery_rate()
        
        health_score = self._calculate_health_score(
            avg_latency,
            delivery_rate
        )
        
        return {
            "health_score": health_score,
            "avg_latency_ms": avg_latency,
            "delivery_rate": delivery_rate,
            "bandwidth_usage": {
                "sent_bytes": self.metrics.bytes_sent,
                "received_bytes": self.metrics.bytes_received,
                "total_messages": self.metrics.sent_messages
            }
        }
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while True:
            try:
                health = await self.get_network_health()
                
                # Check for concerning metrics
                if health["health_score"] < 0.7:
                    await self._trigger_health_alert(health)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(5)
    
    def _calculate_health_score(
        self,
        latency: Optional[float],
        delivery_rate: float
    ) -> float:
        """Calculate overall network health score.
        
        Args:
            latency: Average message latency (ms)
            delivery_rate: Message delivery success rate
            
        Returns:
            Health score between 0 and 1
        """
        scores = [delivery_rate]
        
        if latency is not None:
            # Score latency (lower is better)
            latency_score = max(0, 1 - (latency / 1000))
            scores.append(latency_score)
        
        return statistics.mean(scores)
    
    async def _trigger_health_alert(
        self,
        health_data: Dict[str, Any]
    ) -> None:
        """Trigger health alert callbacks.
        
        Args:
            health_data: Current health metrics
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": "network_health",
            "severity": "warning",
            "metrics": health_data
        }
        
        for callback in self._alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                print(f"Alert callback error: {e}")
