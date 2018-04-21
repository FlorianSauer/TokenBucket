import time
from threading import Lock, Thread

from TokenBucket.TokenBucket import TokenBucket


class App(object):
    def __init__(self):
        self.printlock = Lock()
        pass

    def lockPrint(self, string):
        with self.printlock:
            print string

    def consumeToken(self, bucket, name, testamount):
        # type: (TokenBucket, str, int) -> None
        self.lockPrint("init thread " + name + " tokens to consume: " + str(testamount))
        for i in xrange(testamount):
            bucket.consumeToken(1)
            self.lockPrint("reduced bucket from thread " + name + " tokenid: " + str(i + 1))
        self.lockPrint("thread " + name + " done")

    def debugprint(self, size, refilltime, refillamount, testamount, parallelthreads):
        self.lockPrint("should consume " + str(size) + " tokens")
        self.lockPrint("should wait " + str(refilltime) + " seconds")
        # self.lockPrint(str((((testamount * parallelthreads) - size) / refillamount) + (
        #         ((testamount * parallelthreads) - size) % refillamount)))
        for _ in xrange(((((testamount * parallelthreads) - size) / refillamount) + (
                ((testamount * parallelthreads) - size) % refillamount))-1):
            for i in xrange(refilltime):
                self.lockPrint("waiting... (" + str(i + 1) + ")")
                time.sleep(1)
            self.lockPrint("should refill " + str(refillamount) + " tokens")
            self.lockPrint("should consume " + str(refillamount) + " tokens")
            self.lockPrint("should wait " + str(refilltime) + " seconds")
        for i in xrange(refilltime):
            self.lockPrint("waiting... (" + str(i + 1) + ")")
            time.sleep(1)

    def debugprintOLD(self, size, refilltime, refillamount, testamount, parallelthreads):
        self.lockPrint("Bucket size " + str(size))
        self.lockPrint("refill time " + str(refilltime))
        self.lockPrint("refill amount " + str(refillamount))
        self.lockPrint("tests " + str(testamount))
        self.lockPrint("parallel tests " + str(parallelthreads))
        for _ in xrange(testamount * parallelthreads):
            self.lockPrint("should consume " + str(size) + " tokens")
            self.lockPrint("should wait " + str(refilltime) + " seconds")
            for i in xrange(refilltime):
                self.lockPrint("waiting... (" + str(i + 1) + ")")
                time.sleep(1)
            self.lockPrint("should refill " + str(refillamount) + " tokens")

    def run(self):
        testamount = 10
        parallelthreads = 3
        size = 3
        refilltime = 5
        refillamount = 3
        bucket = TokenBucket(size, refilltime, refillamount, verbose=False)
        if refillamount > size:
            refillamount = size
        self.lockPrint("test parameters:")
        self.lockPrint("Bucket size " + str(size))
        self.lockPrint("refill time " + str(refilltime))
        self.lockPrint("refill amount " + str(refillamount))
        self.lockPrint("tests " + str(testamount))
        self.lockPrint("parallel tests " + str(parallelthreads))
        self.lockPrint("Test threads will consume " + str(testamount * parallelthreads) + " tokens")
        if (((((testamount * parallelthreads) - size) / refillamount) + (
                ((testamount * parallelthreads) - size) % refillamount)) * refilltime) < 0:
            self.lockPrint("test should take " + str(0) + " seconds")
        else:
            self.lockPrint("test should take " + str(((((testamount * parallelthreads) - size) / refillamount) + (
                    ((testamount * parallelthreads) - size) % refillamount)) * refilltime) + " seconds")
        self.lockPrint("")
        self.lockPrint("starting")
        ts = []
        past = time.time()
        t_dp = Thread(target=self.debugprint, args=(size, refilltime, refillamount, testamount, parallelthreads))
        for i in xrange(parallelthreads):
            ts.append(Thread(target=self.consumeToken, args=(bucket, str(i + 1), testamount)))

        t_dp.start()
        for t in ts:
            t.start()

        for t in ts:
            t.join()
        self.lockPrint("that took " + str((time.time() - past)) + " seconds")

        t_dp.join()


if __name__ == "__main__":
    app = App()
    app.run()
