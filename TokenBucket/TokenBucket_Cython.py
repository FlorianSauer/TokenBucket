import sys
import threading
import time


class TokenBucket(object):
    """
    Simple implementation of a synchronized Token Bucket.
    Created mainly for learning purposes.

    Cython Version
    """

    def __init__(self, size, refilltime, refillammount, verbose=False, value=None, lastupdate=None):
        # type: (int, float, int, bool, int, int) -> None
        """
        :param size: The size of the Token Bucket
        :param refilltime: The time interval for refilling the Token Bucket
        :param refillammount: The amount of tokens to refill per refill operation
        :param verbose: Verbosity switch, for debug purposes
        :param value: Initialize the Token Bucket with a given value
        :param lastupdate: Initialize the Token Bucket with a given time
        """

        self.max_amount = size
        self.value = size
        self.refill_time = refilltime
        self.refill_amount = refillammount
        self.mutex = threading.RLock()
        self.last_update = time.time()
        self.verbose = verbose
        if value:
            self.value = value
        if lastupdate:
            self.last_update = lastupdate

    def _refill_count(self, now=None):
        # type: (int) -> int
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

        if self.verbose:
            print "called _refill_count"
        # lastupdate at second 7
        # now is second 15
        # refilltime is 10
        #            (    15     -       7         ) /       10           = 8 / 10 = 0.8 = int 0
        with self.mutex:
            if not now:
                now = time.time()
            return int(((now - self.last_update) / self.refill_time))

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
        # type: (int) -> None
        """
        Performs a refill operation on the Token Bucket.
        The refill operation will only succeede, if the last update is long enough ago.

        :param now: Specifies the current time to use
        """

        if self.verbose:
            print "called refill"
        with self.mutex:
            if not now:
                now = time.time()
            refill_count = self._refill_count(now)  # calculate how many refill operations we can perform
            if refill_count > 0:
                self.value += refill_count * self.refill_amount  # how many items can be refilled

                # amount of refill operations * refilltime -> last update
                # this is a logical calculation, based that time.time() is accurate
                self.last_update += refill_count * self.refill_time

            if self.value > self.max_amount:
                if self.verbose:
                    print "resetting, because self.value", self.value, "> self.size", self.max_amount
                self.value = self.max_amount

    def consumeToken(self, token_amount, blocking=True, timeout=None):
        # type: (int, bool, int) -> bool
        """
        Consumes x tokens from the Token Bucket.
        Per default this method waits and blocks until at least x tokens are available for consuming.

        :param token_amount: amount of tokens to consume
        :param blocking: specifies, if this method should block, until enough tokens are available
        :param timeout: specifies the maximum time to wait, if blocking is enabled
        :return: returns if token_amount tokens could be consumed or not
        """

        if token_amount > self.max_amount:
            print >> sys.stderr, "cannot consume more tokens than bucket size"
            return False

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
                    if self.verbose:
                        print "cannot reduce bucket by more tokens than there are tokens in bucket, try less tokens, current aviable tokens are", self.value
                    return False
                else:  # we enabled to wait for more tokens
                    time_to_wait = now - self.last_update

                    # time delta between now and the last update (could also be negative)
                    if time_to_wait < 0:
                        time_to_wait = 0

                    # theoretical time to wait for additional tokens, substracted by timedelta
                    time_to_wait = (additional_tokes * self.refill_time) - time_to_wait

                    if time_to_wait < 0:
                        time_to_wait = 0
                    if timeout:
                        if time_to_wait > timeout:
                            if self.verbose:
                                print "not enough tokens aviable, waiting would be", time_to_wait, "seconds, but is longer than allowed timeout of", timeout, "seconds, returning"
                            return False

        # due to using 'with mutex' we have to move the following block outside the else block
        # this is VERY ugly, exchange it with mutex.aquire()+mutex.release()
        # will change in the future, maybe
        if self.verbose:
            print "not enough tokens aviable, waiting", time_to_wait, "seconds, so the bucket refills until then"
        time.sleep(time_to_wait)
        return self.consumeToken(token_amount, blocking=blocking,
                                 timeout=timeout)  # lets try again to consume some tokens

    def __enter__(self):
        self.consumeToken(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
