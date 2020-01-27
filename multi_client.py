#!/usr/bin/env python3

import ctypes

import grpc

import value_pb2
import value_pb2_grpc

import logging
import random
import time
import os

from multiprocessing import Process, Value

def setter(addr, rate, end_time, correct):
    delay_sum = 0
    delays = 0
    with grpc.insecure_channel(addr) as channel:
        service = value_pb2_grpc.ValueServiceStub(channel)
        while time.time() < end_time:
            req_start = time.time()
            service.SetValue(value_pb2.Value(value=correct.value))
            req_end = time.time()
            delay = random.expovariate(rate) - (req_start - req_end)
            time.sleep(delay)
            correct.value += 1
            delay_sum += delay
            delays += 1

    with open('setter_stats.txt', 'w') as stats:
       stats.write("delays,delay_sum,mean\n") 
       stats.write("{},{},{}\n".format(delays, delay_sum, delay_sum / delays))


def getter(addr, rate, end_time, correct):
    delay_sum = 0
    delays = 0
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("timestamp,correct,actual")
    with grpc.insecure_channel(addr) as channel:
        service = value_pb2_grpc.ValueServiceStub(channel)
        while time.time() < end_time:
            req_start_ns = time.time_ns()
            req_start = time.time()
            current_correct = correct.value
            actual = service.GetValue(value_pb2.Empty()).value
            req_end = time.time()
            delay = random.expovariate(rate) - (req_start - req_end)
            time.sleep(delay)
            logging.info("%d,%d,%d", req_start_ns, current_correct, actual)
            delay_sum += delay
            delays += 1

    with open('getter_stats.txt', 'w') as stats:
       stats.write("delays,delay_sum,mean\n") 
       stats.write("{},{},{}\n".format(delays, delay_sum, delay_sum / delays))


if __name__ == "__main__":
    random.seed(int(os.getenv("SEED", 42)))

    correct = Value('I', 1)

    addr = os.getenv("VALUE_SERVICE_ADDR", "localhost:1100")
    set_rate = float(os.getenv("SET_RATE", 20.0))
    get_rate = float(os.getenv("GET_RATE", 20.0))
    end_time = time.time() + float(os.getenv("DURATION", 300))

    set_process = Process(target=setter, args=(addr, set_rate, end_time, correct))
    set_process.start()

    get_process = Process(target=getter, args=(addr, get_rate, end_time, correct))
    get_process.start()

    set_process.join()
    get_process.join()
    
