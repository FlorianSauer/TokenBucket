import threading
import time

from TokenBucketErrors import TimeoutError, TokenAmountError, BucketSizeError


class TokenBucket(object):
    """
    Simple implementation of a synchronized Token Bucket.
    Created mainly for learning purposes.
    """

    def __init__(self, size, refillrate, refillamount, value=None, lastupdate=None):
        # type: (int, float, int, int, float) -> None
        """
        :param size: The size of the Token Bucket
        :param refillrate: The time interval for refilling the Token Bucket
        :param refillamount: The amount of tokens to refill per refill operation
        :param value: Initialize the Token Bucket with a given value
        :param lastupdate: Initialize the Token Bucket with a given timestamp
        """

        self.size = size  # type: int
        self.value = size  # type: int
        self.refill_rate = refillrate  # type: float
        self.refill_amount = refillamount  # type: int
        self.mutex = threading.RLock()  # type: threading.RLock
        self.last_update = time.time()  # type: float
        if value:
            self.value = value  # type: int
        if lastupdate:
            self.last_update = lastupdate  # type: float

    def _refill_count(self, now=None):
        # type: (float) -> int
        """
        calculate the amount of refill operations that can be executed,
        within the time period | last update -> now |
        calculated via ( (now - last update time) / refill time ) as int()

        Example:
        last update at second 7
        now is second 15
        refill time is 10

          ( 15 - 7 ) / 10
        =      8     / 10
        = 0.8
        = int 0

        :param now: Specifies the current time to use
        :return: The amount of refill operations
        """

        # lastupdate at second 7
        # now is second 15
        # refilltime is 10
        #            (    15     -       7         ) /       10           = 8 / 10 = 0.8 = int 0
        with self.mutex:
            if not now:
                now = time.time()  # type: float
            return int(((now - self.last_update) / self.refill_rate))

    def current_filllevel(self):
        # type: () -> int
        """
        returns the current fill level of the Token Bucket (self.value).
        refills bucket automatically, so the returned value is more up to date.

        :return: the current fill level of the Token Bucket
        """

        with self.mutex:
            self.refill()  # refilling inside mutex, because another thread could jump between refill() and return value
            return self.value

    def refill(self, now=None):
        # type: (float) -> None
        """
        Performs a refill operation on the Token Bucket.
        The refill operation will only succeed, if the last update is long enough ago.

        :param now: Specifies the current time to use
        """

        with self.mutex:
            if not now:
                now = time.time()  # type: float
            refill_count = self._refill_count(now)  # calculate how many refill operations we can perform
            if refill_count > 0:
                self.value += refill_count * self.refill_amount  # how many items can be refilled

                # amount of refill operations * refilltime -> last update
                # this is a logical calculation, based that time.time() is accurate
                self.last_update += refill_count * self.refill_rate

            if self.value > self.size:
                self.value = self.size

    def consumeToken(self, token_amount, blocking=True, timeout=None):
        # type: (int, bool, float) -> bool
        """
        Consumes x tokens from the Token Bucket.
        Per default this method waits and blocks until at least x tokens are available for consuming.

        :param token_amount: amount of tokens to consume
        :param blocking: specifies, if this method should block, until enough tokens are available
        :param timeout: specifies the maximum time to wait, if blocking is enabled
        :return: returns if token_amount tokens could be consumed or not
        :raises BucketSizeError: a BucketSizeError is raised, if the given token_amount is bigger than the maximum
        bucket size
        :raises TokenAmountError: a TokenAmountError is raised, if the current amount of tokens in the Bucket is
        smaller than token_amount and blocking is set to False
        :raises TimeoutError: a TimeoutError is raised, if the bucket has not enough tokens and the time to wait for a
        sufficient amount of tokens woould take longer than the given timeout
        """

        if token_amount > self.size:
            raise BucketSizeError("cannot consume more tokens than the maximum amount of tokens in the bucket")

        with self.mutex:
            now = time.time()
            self.refill(now)  # perform a refill, before we consume tokens, maybe we have gained some more tokens

            # we want to consume less tokens than there are tokens currently in the bucket, nice case
            if token_amount <= self.value:
                self.value -= token_amount
                return True
            else:  # we want to consume more tokens, than there are tokens in the bucket, bad case
                additional_tokes = token_amount - self.value  # the ammount of tokens we are short
                if not blocking:
                    raise TokenAmountError(
                        "cannot reduce bucket by more tokens than there are tokens in bucket, try less tokens, current aviable tokens are " + str(
                            self.value))
                else:  # we enabled to wait for more tokens
                    time_to_wait = now - self.last_update

                    # time delta between now and the last update (could also be negative)
                    if time_to_wait < 0:
                        time_to_wait = 0

                    # theoretical time to wait for additional tokens, substracted by timedelta
                    time_to_wait = (additional_tokes * self.refill_rate) - time_to_wait

                    if time_to_wait < 0:
                        time_to_wait = 0
                    if timeout:
                        if time_to_wait > timeout:
                            raise TimeoutError("not enough tokens aviable, waiting would be " + str(
                                time_to_wait) + " seconds, but is longer than allowed timeout of " + str(
                                timeout) + " seconds, returning")

        # due to using 'with mutex' we have to move the following block outside the else block
        # this is VERY ugly, exchange it with mutex.aquire()+mutex.release()
        # will change in the future, maybe
        time.sleep(time_to_wait)
        if timeout:
            timeout = timeout - time_to_wait
        return self.consumeToken(token_amount, blocking=blocking,
                                 timeout=timeout)  # lets try again to consume some tokens

    def __enter__(self):
        self.consumeToken(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
