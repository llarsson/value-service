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
    gets = caching.query('method == "/ValueService/GetValue()"')
    cached = gets.query('source == "cache"').shape[0]
    total = gets.shape[0]
    return cached / total


def calculate_server_work_fraction(client, server):
    gets_at_server = server.query('operation == "get"')
    return gets_at_server.shape[0] / client.shape[0]


def calculate_goodness(error_fraction, traffic_reduction, server_work_fraction):
    alpha = np.log(2)
    beta = np.log(2)
    gamma = 2
    return np.exp(alpha * (traffic_reduction - 1.0)) * np.exp(-beta * server_work_fraction) * (1.0 - np.power(error_fraction, 1.0/gamma))


def averages(algorithm, phase, client, caching, estimator, server):
    error_fraction = calculate_error_fraction(client)
    traffic_reduction = calculate_traffic_reduction(caching)
    server_work_fraction = calculate_server_work_fraction(client, server)
    goodness = calculate_goodness(error_fraction, traffic_reduction, server_work_fraction)

    results = pd.DataFrame([[algorithm, phase, error_fraction, traffic_reduction, server_work_fraction, goodness]], 
            columns=['algorithm', 'phase', 'error_fraction', 'traffic_reduction', 'server_work_fraction', 'goodness'])
    results.set_index('algorithm', inplace=True)
    return results


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

    results = averages(algorithm, phase, client, caching, estimator, server)

    print(results.to_csv(None))
