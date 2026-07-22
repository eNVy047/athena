import pytest
import asyncio
from friday.reliability.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from friday.reliability.retry_manager import RetryManager

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    
    async def failing_call():
        raise ValueError("Simulated failure")
        
    with pytest.raises(ValueError):
        await cb.call(failing_call)
    with pytest.raises(ValueError):
        await cb.call(failing_call)
        
    # Threshold reached, should be open
    with pytest.raises(CircuitBreakerOpenException):
        await cb.call(failing_call)
        
    # Wait for recovery
    await asyncio.sleep(0.15)
    
    # Should be half-open and fail normally
    with pytest.raises(ValueError):
        await cb.call(failing_call)

@pytest.mark.asyncio
async def test_retry_manager():
    attempts = 0
    async def flaky_call():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Fail")
        return "Success"
        
    result = await RetryManager.with_retry(
        flaky_call, max_retries=3, initial_backoff=0.01, exceptions=(ValueError,)
    )
    assert result == "Success"
    assert attempts == 3
