from typing import Callable

from tenacity import Retrying, stop_after_attempt, wait_exponential


def call_with_retry(call: Callable, attempts: int = 3, base_wait: float = 1.0):
    """Run `call`, retrying with exponential backoff; re-raises the last error."""
    retrying = Retrying(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=base_wait, max=10),
        reraise=True,
    )
    return retrying(call)
