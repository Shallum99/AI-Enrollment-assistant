# app/core/monitoring.py
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ServiceMetrics:
    """Data class for service metrics"""
    service_name: str
    start_time: datetime = field(default_factory=datetime.now)
    requests_total: int = 0
    requests_success: int = 0
    requests_error: int = 0
    response_times: List[float] = field(default_factory=list)
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    @property
    def uptime_seconds(self) -> float:
        """Get uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def uptime_formatted(self) -> str:
        """Get formatted uptime string"""
        seconds = self.uptime_seconds
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    @property
    def avg_response_time(self) -> Optional[float]:
        """Get average response time"""
        if not self.response_times:
            return None
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def success_rate(self) -> Optional[float]:
        """Get success rate as percentage"""
        if self.requests_total == 0:
            return None
        return (self.requests_success / self.requests_total) * 100
    
    def record_request(self, success: bool, response_time: float, error: Optional[str] = None):
        """Record a request"""
        self.requests_total += 1
        
        if success:
            self.requests_success += 1
        else:
            self.requests_error += 1
            self.last_error = error
            self.last_error_time = datetime.now()
        
        # Keep last 100 response times for average calculation
        self.response_times.append(response_time)
        if len(self.response_times) > 100:
            self.response_times.pop(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "service_name": self.service_name,
            "start_time": self.start_time.isoformat(),
            "uptime": self.uptime_formatted,
            "requests": {
                "total": self.requests_total,
                "success": self.requests_success,
                "error": self.requests_error,
                "success_rate": f"{self.success_rate:.2f}%" if self.success_rate is not None else "N/A"
            },
            "response_time": {
                "average": f"{self.avg_response_time:.2f}ms" if self.avg_response_time is not None else "N/A",
                "samples": len(self.response_times)
            },
            "last_error": {
                "message": self.last_error,
                "time": self.last_error_time.isoformat() if self.last_error_time else None
            }
        }

class ServiceMonitor:
    """Service monitoring utility"""
    
    def __init__(self):
        """Initialize the service monitor"""
        self.services: Dict[str, ServiceMetrics] = {}
        self.start_time = datetime.now()
    
    def register_service(self, service_name: str) -> ServiceMetrics:
        """Register a service for monitoring"""
        if service_name in self.services:
            logger.warning(f"Service {service_name} already registered")
            return self.services[service_name]
        
        self.services[service_name] = ServiceMetrics(service_name=service_name)
        logger.info(f"Registered service for monitoring: {service_name}")
        return self.services[service_name]
    
    def get_service_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """Get metrics for a specific service"""
        return self.services.get(service_name)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all services"""
        return {
            service_name: metrics.to_dict() 
            for service_name, metrics in self.services.items()
        }
    
    def record_request(
        self, 
        service_name: str, 
        success: bool, 
        response_time: float, 
        error: Optional[str] = None
    ):
        """Record a request for a service"""
        if service_name not in self.services:
            logger.warning(f"Service {service_name} not registered, registering now")
            self.register_service(service_name)
        
        self.services[service_name].record_request(
            success=success,
            response_time=response_time,
            error=error
        )
    
    async def monitor_task(self, interval_seconds: int = 300):
        """Background task to log periodic service status"""
        logger.info("Starting service monitoring task")
        
        while True:
            try:
                # Wait for the specified interval
                await asyncio.sleep(interval_seconds)
                
                # Log status for each service
                for service_name, metrics in self.services.items():
                    logger.info(
                    f"Service {service_name}: "
                    f"Uptime {metrics.uptime_formatted}, "
                    f"Requests {metrics.requests_total}, "
                    f"Success rate {metrics.success_rate:.2f}% if metrics.success_rate is not None else 'N/A', "
                    f"Avg response time {metrics.avg_response_time:.2f}ms if metrics.avg_response_time is not None else 'N/A'")
            except Exception as e:
                logger.error(f"Error in monitoring task: {str(e)}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        # This would include CPU, memory, etc. in a production system
        # For now, just return basic info
        return {
            "start_time": self.start_time.isoformat(),
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "services_count": len(self.services),
            "total_requests": sum(s.requests_total for s in self.services.values())
        }

# Initialize service monitor
service_monitor = ServiceMonitor()

# Register core services
service_monitor.register_service("voice")
service_monitor.register_service("browser")
service_monitor.register_service("email")
service_monitor.register_service("workflow")

# Decorator for monitoring service functions
def monitor_service(service_name: str):
    """Decorator to monitor service function execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error = None
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                service_monitor.record_request(
                    service_name=service_name,
                    success=success,
                    response_time=response_time,
                    error=error
                )
        
        return wrapper
    return decorator