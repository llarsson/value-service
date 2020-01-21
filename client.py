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

def run(addr, mean):
    with grpc.insecure_channel(addr) as channel:
        service = value_pb2_grpc.ValueServiceStub(channel)
        while (True):
            correct = random.randint(1, 100000000)
            service.SetValue(value_pb2.Value(value=correct))
            delay()

            requests = int(random.expovariate(1/mean))
            while requests:
                actual = service.GetValue(value_pb2.Empty()).value
                logging.info("%d,%d", correct, actual)
                delay()
                requests -= 1

if __name__=="__main__":
    random.seed(int(os.getenv("SEED", 42)))
    logging.basicConfig(format='%(asctime)s,%(message)s', datefmt='%s', level=logging.INFO)
    run(os.getenv("VALUE_SERVICE_ADDR", "localhost:1111"), os.getenv("MEAN", 20.0))
