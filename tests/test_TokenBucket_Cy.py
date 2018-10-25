import time
from unittest import TestCase
from TokenBucket.TokenBucket_cy import TokenBucket
from TokenBucket.TokenBucketErrors import BucketSizeError, TimeoutError, TokenAmountError, TokenBucketError
from TestDefaults import *

class TestTokenBucket(TestCase):
    def test_consumeToken(self):
        bucket = TokenBucket(
            size=DEFAULT_BUCKET_SIZE,
            refillrate=DEFAULT_REFILL_TIME,
            refillamount=DEFAULT_REFILL_AMOUNT
        )
        bucket.consumeToken(DEFAULT_BUCKET_SIZE, )
        # bucket.consumeToken(1, blocking=False)
        self.assertRaises(TokenAmountError, bucket.consumeToken, 1, blocking=False)
        self.assertRaises(BucketSizeError, bucket.consumeToken, DEFAULT_BUCKET_SIZE+1, blocking=False)
        self.assertRaises(TimeoutError, bucket.consumeToken, 1, timeout=1.0)

    def test_current_filllevel(self):
        bucket = TokenBucket(
            size=DEFAULT_BUCKET_SIZE,
            refillrate=DEFAULT_REFILL_TIME,
            refillamount=DEFAULT_REFILL_AMOUNT
        )
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE)
        bucket.consumeToken(1)
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE-1)
        bucket.consumeToken(2)
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE-3)
        bucket.consumeToken(1)  # bucket is empty, will wait for refill and consume 1 token
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE-1)
        bucket.consumeToken(2)
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE-3)

    def test_refill(self):
        bucket = TokenBucket(
            size=DEFAULT_BUCKET_SIZE,
            refillrate=DEFAULT_REFILL_TIME,
            refillamount=DEFAULT_REFILL_AMOUNT
        )
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE)
        bucket.consumeToken(1)
        bucket.refill(force=True)
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE)
        bucket.consumeToken(2)
        bucket.refill(force=True)
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE)
        bucket.consumeToken(3)
        bucket.refill(force=True)
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE)
        bucket.consumeToken(1)
        bucket.consumeToken(2)
        bucket.refill(force=True)
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE)
        bucket.consumeToken(1)
        bucket.refill(now=time.time())
        self.assertEqual(bucket.current_filllevel(), DEFAULT_BUCKET_SIZE-1)

    def test_consumeTokenTimeNiceCase(self):
        """
        tests if the refill time is correct
        """
        bucket = TokenBucket(
            size=DEFAULT_BUCKET_SIZE,
            refillrate=DEFAULT_REFILL_TIME,
            refillamount=DEFAULT_REFILL_AMOUNT
        )
        past = time.time()
        bucket.consumeToken(DEFAULT_BUCKET_SIZE)
        present = time.time()
        self.assertAlmostEqual(0, present-past)
        past = time.time()
        bucket.consumeToken(DEFAULT_REFILL_AMOUNT)
        present = time.time()
        self.assertAlmostEqual(DEFAULT_REFILL_TIME, present-past, places=2)

    def test_consumeTokenTimeWorstCase(self):
        """
        tests if the refill time is correct
        """
        bucket = TokenBucket(
            size=DEFAULT_BUCKET_SIZE*2,
            refillrate=DEFAULT_REFILL_TIME,
            refillamount=DEFAULT_REFILL_AMOUNT
        )
        past = time.time()
        bucket.consumeToken(DEFAULT_BUCKET_SIZE*2)
        present = time.time()
        self.assertAlmostEqual(0, present-past, places=4)
        past = time.time()
        bucket.consumeToken(DEFAULT_REFILL_AMOUNT+1)
        present = time.time()
        self.assertAlmostEqual(DEFAULT_REFILL_TIME*2, present-past, places=2)

    def test_consumeTokenTimeAverageCase(self):
        """
        tests if the refill time is correct
        """
        bucket = TokenBucket(
            size=DEFAULT_BUCKET_SIZE*2,
            refillrate=DEFAULT_REFILL_TIME,
            refillamount=DEFAULT_REFILL_AMOUNT
        )
        past = time.time()
        bucket.consumeToken(DEFAULT_BUCKET_SIZE)
        present = time.time()
        self.assertAlmostEqual(0, present-past, places=4)
        # bucket is now half full
        past = time.time()
        bucket.consumeToken(DEFAULT_BUCKET_SIZE*2)  # request full bucket
        present = time.time()
        self.assertAlmostEqual(DEFAULT_REFILL_TIME, present-past, places=2)  # must refill at least once