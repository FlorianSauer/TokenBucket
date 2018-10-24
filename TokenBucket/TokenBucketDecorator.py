import wrapt
from typing import Callable

from . import TokenBucket


def withTokenBucket(bucket, token_amount=1, blocking=True, timeout=None):
    # type: (TokenBucket, int, bool, float) -> Callable

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        bucket.consumeToken(token_amount=token_amount, blocking=blocking, timeout=timeout)
        return wrapped(*args, **kwargs)

    return wrapper
