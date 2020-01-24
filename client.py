#!/usr/bin/env python3

import grpc

import value_pb2
import value_pb2_grpc

import logging
import random
import time
import os

def delay():
    time.sleep(1)

def run(addr, mean, max_count):
    with grpc.insecure_channel(addr) as channel:
        service = value_pb2_grpc.ValueServiceStub(channel)
        correct = 0
        count = 0
        while count <= max_count:
            count += 1
            correct += 1
            service.SetValue(value_pb2.Value(value=correct))
            delay()

            requests = int(random.expovariate(1/mean)) + 1
            while requests and count <= max_count:
                count += 1
                actual = service.GetValue(value_pb2.Empty()).value
                logging.info("%d,%d,%d", time.time_ns(), correct, actual)
                requests -= 1
                if requests:
                    delay()

if __name__=="__main__":
    random.seed(int(os.getenv("SEED", 42)))
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("timestamp,correct,actual")
    run(os.getenv("VALUE_SERVICE_ADDR", "localhost:1100"), 
            float(os.getenv("MEAN", 20.0)),
            int(os.getenv("COUNT", 300)))
