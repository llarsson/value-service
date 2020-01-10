#!/usr/bin/env python3

import grpc
from concurrent import futures

import value_pb2 as pb
import value_pb2_grpc as stub

import logging

class ValueServiceServicer(stub.ValueServiceServicer):
    def __init__(self):
        self.value = 1

    def GetValue(self, request, context):
        result = pb.Value(value=self.value)
        logging.info("get,%d", result.value)
        return result

    def SetValue(self, request, context):
        self.value = request.value.value
        logging.info("set,%d", self.value)

def serve(port):
    # single-threaded for dependable results
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    stub.add_ValueServiceServicer_to_server(ValueServiceServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    server.start()
    server.wait_for_termination()

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s,%(message)s', datefmt='%s', level=logging.INFO)
    serve(8080)