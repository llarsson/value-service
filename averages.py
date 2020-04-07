#!/usr/bin/env python3

import pandas as pd
import numpy as np

import sys

def calculate_error_fraction(client):
    client['difference'] = client['correct'] - client['actual']
    client['errors'] = client['difference'].clip(0,1)
    error_count = client['errors'].sum() # since either 0 or 1
    error_fraction = error_count / client.shape[0]
    return error_fraction


def calculate_traffic_reduction(caching):
    upstream_gets = caching.query('source == "upstream"').query('method == "/ValueService/GetValue(0)"')
    cache_gets = caching.query('source == "cache"').query('method == "/ValueService/GetValue"')
    total_count = upstream_gets.shape[0] + cache_gets.shape[0]
    return cache_gets.shape[0] / total_count


def calculate_server_work_fraction(client, server):
    gets_at_server = server.query('operation == "get"')
    return gets_at_server.shape[0] / client.shape[0]


def calculate_goodness(error_fraction, traffic_reduction, server_work_fraction):
    alpha = np.log(2)
    beta = np.log(2)
    gamma = 2
    return np.exp(alpha * (traffic_reduction - 1.0)) * np.exp(-beta * server_work_fraction) * (1.0 - np.power(error_fraction, 1.0/gamma))


def averages(experiment_count, algorithm, phase, client, caching, estimator, server):
    error_fraction = calculate_error_fraction(client)
    traffic_reduction = calculate_traffic_reduction(caching)
    server_work_fraction = calculate_server_work_fraction(client, server)
    goodness = calculate_goodness(error_fraction, traffic_reduction, server_work_fraction)
    (client_gets, caching_gets, estimator_incoming_gets, estimator_verification_gets, server_gets) = parse_gets(experiment_count, client, caching, estimator, server)

    results = pd.DataFrame([[algorithm, phase, client_gets, caching_gets, estimator_incoming_gets, estimator_verification_gets, server_gets, error_fraction, traffic_reduction, server_work_fraction, goodness]], 
            columns=['algorithm', 'phase', 'client_gets', 'caching_gets', 'estimator_incoming_gets', 'estimator_verification_gets', 'server_gets', 'error_fraction', 'traffic_reduction', 'server_work_fraction', 'goodness'])
    results.set_index(['algorithm', 'phase'], inplace=True)
    return results


def parse_gets(experiment_count, client, caching, estimator, server):
    client_gets = client.shape[0] / experiment_count
    caching_gets = caching.query('method == "/ValueService/GetValue(0)"').shape[0] / experiment_count
    estimator_incoming_gets = estimator.query('method == "/ValueService/GetValue(0)"').query('source == "client"').shape[0] / experiment_count
    estimator_verification_gets = estimator.query('method == "/ValueService/GetValue(0)"').query('source == "verifier"').shape[0] / experiment_count
    server_gets = server.query('operation == "get"').shape[0] / experiment_count

    return (client_gets, caching_gets, estimator_incoming_gets, estimator_verification_gets, server_gets)


if __name__=="__main__":
    algorithm = sys.argv[1]
    phase = sys.argv[2]
    experiments = sys.argv[3:]

    client_sources = []
    caching_sources = []
    estimator_sources = []
    server_sources = []

    for experiment in experiments:
        client_sources.append(pd.read_csv(experiment + '/client.log'))
        caching_sources.append(pd.read_csv(experiment + '/caching.csv'))
        estimator_sources.append(pd.read_csv(experiment + '/estimator.csv'))
        server_sources.append(pd.read_csv(experiment + '/server.log'))

    client = pd.concat(client_sources)
    client.set_index('timestamp')

    caching = pd.concat(caching_sources)
    caching.set_index('timestamp')

    estimator = pd.concat(estimator_sources)
    estimator.set_index('timestamp')

    server = pd.concat(server_sources)
    server.set_index('timestamp')

    results = averages(len(experiments), algorithm, phase, client, caching, estimator, server)

    print(results.to_csv(None))
