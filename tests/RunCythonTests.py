import threading
import time

from TokenBucket.TokenBucket_Cython import TokenBucket

printlock = threading.Lock()


def consumeToken(bucket, name, iterations):
    # type: (TokenBucket, str, int) -> None
    for _ in xrange(iterations):
        bucket.consumeToken(1)
        with printlock:
            print "reduced bucket from thread " + name


if __name__ == "__main__":

    iterations = 3
    parallelthreads = 5

    size = 3
    refillrate = 5
    refillamount = 3

    bucket = TokenBucket(size, refillrate, refillamount, verbose=False)
    threads = []  # type: list[threading.Thread]

    print "init bucket with a total size of", bucket.size
    print "init bucket with a refill rate of", bucket.refill_rate
    print "init bucket with a refill amount of", bucket.refill_amount

    print "this test will consume a total amount of", (iterations * parallelthreads), "tokens"
    print "this test should take at least", (((iterations * parallelthreads) / refillamount) * refillrate) - refillrate, "seconds"

    past = time.time()

    print
    print "starting test"
    print

    for i in xrange(parallelthreads):
        t = threading.Thread(target=consumeToken, args=(bucket, str(i), iterations))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print "that took", (time.time() - past), 'seconds'
