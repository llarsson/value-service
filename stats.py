#!/usr/bin/env python3

import pandas as pd

import sys

def calculate_error_fraction(client):
    client['difference'] = client['correct'] - client['actual']
    client['errors'] = client['difference'].clip(0,1)
    error_count = client['errors'].sum() # since either 0 or 1
    error_fraction = error_count / client.shape[0]
    return error_fraction

def calculate_mean_response_time(client):
    return client['response_time'].mean()


def calculate_traffic_reduction(caching):
    gets = caching.query('method == "/ValueService/GetValue()"')
    cached = gets.query('source == "cache"')
    total = gets.shape[0]
    return cached.shape[0] / total


def calculate_mean_ttl(estimator):
    return estimator['estimate'].mean()


def main(experiment):
    client = pd.read_csv(experiment + '/client.log')
    caching = pd.read_csv(experiment + '/caching.csv')
    estimator = pd.read_csv(experiment + '/estimator.csv')
    server = pd.read_csv(experiment + '/server.log')

    error_fraction = calculate_error_fraction(client)
    traffic_reduction = calculate_traffic_reduction(caching)
    mean_ttl = calculate_mean_ttl(estimator)
    mean_response_time = calculate_mean_response_time(client)

    print('{},{},{},{}'.format(error_fraction, traffic_reduction, mean_ttl, mean_response_time))


if __name__=="__main__":
    main(sys.argv[1])
