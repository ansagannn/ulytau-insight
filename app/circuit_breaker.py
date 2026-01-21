import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 1800):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0
        
    def allow_request(self) -> bool:
        """
        Check if request is allowed based on state.
        Handles auto-transition from OPEN to HALF_OPEN after timeout.
        """
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("CircuitBreaker: State changed to HALF_OPEN (probing...)")
                return True
            return False
            
        if self.state == CircuitState.HALF_OPEN:
            # We allow one request to probe.
            # Real implementation might need lock, but for simple sync/async usage this is okay.
            return True
            
        return False

    def record_success(self):
        """
        Call on successful request. 
        Resets failures and closes circuit.
        """
        if self.state != CircuitState.CLOSED:
            logger.info("CircuitBreaker: Success! State changed to CLOSED.")
            self.state = CircuitState.CLOSED
            self.failures = 0

    def record_failure(self):
        """
        Call on failed request.
        Increments failures and opens circuit if threshold reached.
        """
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"CircuitBreaker: Threshold reached ({self.failures}). State changed to OPEN.")
        
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("CircuitBreaker: Probe failed. State changed back to OPEN.")
