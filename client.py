#!/usr/bin/env python3

import grpc

import value_pb2 as pb
import value_pb2_grpc as stub

import logging
import random
import time

def should_update_value():
    return False

def delay():
    time.sleep(1)

def run(port):
    with grpc.insecure_channel("localhost:{}".format(port)) as channel:
        service = stub.ValueServiceStub(channel)
        correct = service.GetValue(pb.Empty()).value
        while (True):
            if should_update_value():
                correct = random.randint(1, 100000000)
                service.SetValue(pb.Value(value=correct))
            delay()
            actual = service.GetValue(pb.Empty()).value
            logging.info("%d,%d", correct, actual)

if __name__=="__main__":
    random.seed(10)
    logging.basicConfig(format='%(asctime)s,%(message)s', datefmt='%s', level=logging.INFO)
    run(8080)