#!/usr/bin/env python3

import ctypes

import grpc

import value_pb2
import value_pb2_grpc

import logging
import math
import random
import time
import os

from multiprocessing import Process, Value

time_zero = time.time()
time_zero_ns = time.time_ns()

def now():
    return time.time() - time_zero

def now_ns():
    return time.time_ns() - time_zero_ns

def setter(addr, end_time, correct, delay_function):
    random.seed(int(os.getenv("SEED", 42)))
    delay_sum = 0
    delays = 0
    with grpc.insecure_channel(addr) as channel:
        service = value_pb2_grpc.ValueServiceStub(channel)
        while now() < end_time:
            req_start = now()
            service.SetValue(value_pb2.Value(value=correct.value))
            req_end = now()
            delay = delay_function(req_end) - (req_start - req_end)
            time.sleep(delay)
            correct.value += 1
            delay_sum += delay
            delays += 1

    with open('setter_stats.txt', 'w') as stats:
       stats.write("delays,delay_sum,mean\n") 
       stats.write("{},{},{}\n".format(delays, delay_sum, delay_sum / delays))


def getter(addr, end_time, correct, delay_function):
    random.seed(int(os.getenv("SEED", 42)))
    delay_sum = 0
    delays = 0
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("timestamp,response_time,correct,actual")
    with grpc.insecure_channel(addr) as channel:
        service = value_pb2_grpc.ValueServiceStub(channel)
        while now() < end_time:
            try: 
                work_start = now()
                # fetch current correct value before making actual request,
                # since this could take a while due to thread safety and whatnot
                current_correct = correct.value

                req_start_ns = now_ns()
                actual = service.GetValue(value_pb2.Empty()).value
                req_end_ns = now_ns()
                logging.info("%d,%d,%d,%d", req_start_ns, (req_end_ns - req_start_ns), current_correct, actual)

                delays += 1
                # delay must be proportional to the time it took to make request
                work_end = now()
                delay = delay_function(work_end) - (work_start - work_end)
                delay_sum += delay
                time.sleep(delay)
            except:
                continue


    with open('getter_stats.txt', 'w') as stats:
       stats.write("delays,delay_sum,mean\n") 
       stats.write("{},{},{}\n".format(delays, delay_sum, delay_sum / delays))

def poisson(rate):
    def f(time):
        return random.expovariate(rate)
    return f

def sinusodial(min_rate, max_rate, period, phase):
    b = min_rate
    a = (max_rate - b) / 2.0
    def f(time):
        y = a + b + a * math.sin(time * 2 * math.pi / period + phase)
        return random.expovariate(y)
    return f

if __name__ == "__main__":
    correct = Value('I', 1)

    addr = os.getenv("VALUE_SERVICE_ADDR", "localhost:1100")
    end_time = now() + float(os.getenv("DURATION", 300))

    get_mode = os.getenv("GETTER_MODE", "poisson")
    set_mode = os.getenv("SETTER_MODE", "poisson")

    getter_poisson_rate = float(os.getenv("GETTER_POISSON_RATE", 20.0))
    setter_poisson_rate = float(os.getenv("SETTER_POISSON_RATE", 20.0))

    getter_sinusodial_min_rate = float(os.getenv("GETTER_SINUSODIAL_MIN_RATE", 1))
    getter_sinusodial_max_rate = float(os.getenv("GETTER_SINUSODIAL_MAX_RATE", 10))
    getter_sinusodial_period = float(os.getenv("GETTER_SINUSODIAL_PERIOD", 1200))
    getter_sinusodial_phase = float(os.getenv("GETTER_SINUSODIAL_PHASE", 0))

    setter_sinusodial_min_rate = float(os.getenv("SETTER_SINUSODIAL_MIN_RATE", 0.05))
    setter_sinusodial_max_rate = float(os.getenv("SETTER_SINUSODIAL_MAX_RATE", 1))
    setter_sinusodial_period = float(os.getenv("SETTER_SINUSODIAL_PERIOD", 1200))
    setter_sinusodial_phase = float(os.getenv("SETTER_SINUSODIAL_PHASE", 0))

    getter_delay_function = None
    if get_mode == "sinusodial":
        getter_delay_function = sinusodial(getter_sinusodial_min_rate, 
                getter_sinusodial_max_rate, getter_sinusodial_period,
                getter_sinusodial_phase)
    else:
        getter_delay_function = poisson(getter_poisson_rate)

    setter_delay_function = None
    if set_mode == "sinusodial":
        setter_delay_function = sinusodial(setter_sinusodial_min_rate, 
                setter_sinusodial_max_rate, setter_sinusodial_period,
                setter_sinusodial_phase)
    else:
        setter_delay_function = poisson(setter_poisson_rate)

    set_process = Process(target=setter, args=(addr, end_time, correct, setter_delay_function))
    set_process.start()

    get_process = Process(target=getter, args=(addr, end_time, correct, getter_delay_function))
    get_process.start()

    set_process.join()
    get_process.join()
    
