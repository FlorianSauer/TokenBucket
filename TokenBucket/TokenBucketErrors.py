class TokenBucketError(Exception):
    pass


class TimeoutError(TokenBucketError):
    pass


class TokenAmountError(TokenBucketError):
    pass


class BucketSizeError(TokenBucketError):
    pass
