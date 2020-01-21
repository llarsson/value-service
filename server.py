#!/usr/bin/env python3

import grpc
from concurrent import futures

import value_pb2
import value_pb2_grpc

import logging
import os

class ValueServiceServicer(value_pb2_grpc.ValueServiceServicer):
    def __init__(self):
        self.value = 1

    def GetValue(self, request, context):
        result = value_pb2.Value()
        result.value = self.value
        logging.info("get,%d", self.value)
        return result

    def SetValue(self, request, context):
        self.value = request.value
        logging.info("set,%d", self.value)
        return value_pb2.Empty()

def serve(port):
    # single-threaded for dependable results
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    value_pb2_grpc.add_ValueServiceServicer_to_server(ValueServiceServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s,%(message)s', datefmt='%s', level=logging.INFO)
    serve(int(os.getenv("PORT", 1111)))