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
    random.seed(int(os.getenv("SEED", 42)))
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
    random.seed(int(os.getenv("SEED", 42)))
    delay_sum = 0
    delays = 0
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("timestamp,response_time,correct,actual")
    with grpc.insecure_channel(addr) as channel:
        service = value_pb2_grpc.ValueServiceStub(channel)
        while time.time() < end_time:
            try: 
                work_start = time.time()
                # fetch current correct value before making actual request,
                # since this could take a while due to thread safety and whatnot
                current_correct = correct.value

                req_start_ns = time.time_ns()
                actual = service.GetValue(value_pb2.Empty()).value
                req_end_ns = time.time_ns()
                logging.info("%d,%d,%d,%d", req_start_ns, (req_end_ns - req_start_ns), current_correct, actual)

                delays += 1
                # delay must be proportional to the time it took to make request
                work_end = time.time()
                delay = random.expovariate(rate) - (work_start - work_end)
                delay_sum += delay
                time.sleep(delay)
            except:
                continue


    with open('getter_stats.txt', 'w') as stats:
       stats.write("delays,delay_sum,mean\n") 
       stats.write("{},{},{}\n".format(delays, delay_sum, delay_sum / delays))


if __name__ == "__main__":
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
    
