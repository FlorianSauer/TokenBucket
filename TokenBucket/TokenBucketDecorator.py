import wrapt
from typing import Callable

from . import TokenBucket
# noinspection PyUnresolvedReferences
from .TokenBucketErrors import TimeoutError, BucketSizeError, TokenAmountError


def withTokenBucket(bucket, token_amount=1, blocking=True, timeout=None):
    # type: (TokenBucket, int, bool, float) -> Callable
    """
    Decorator to limit a function with a TokenBucket

    :param bucket: The TokenBucket to use
    :param token_amount: The amount of tokens to consume for one function call
    :param blocking: If the token requiring process should block
    :param timeout: The timeout to use for requiring a token
    :exception TimeoutError: The time to require all needed tokes exceeds the given timeout
    :exception BucketSizeError: The amount of tokens to acquire for a function call exceeds the TokenBucket Size
    :exception TokenAmountError: Raised when token acquiring is not in blocking mode. Required token amount for a
                                 function call exceeds the current fill level of the bucket
    """

    # noinspection PyUnusedLocal
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        bucket.consumeToken(token_amount=token_amount, blocking=blocking, timeout=timeout)
        return wrapped(*args, **kwargs)

    return wrapper
