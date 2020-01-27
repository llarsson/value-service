#!/usr/bin/env python3

import pandas as pd

import sys

def calculate_error_fraction(client):
    client['difference'] = client['correct'] - client['actual']
    client['errors'] = client['difference'].clip(0,1)
    error_count = client['errors'].sum() # since either 0 or 1
    error_fraction = error_count / client.shape[0]
    return error_fraction


def calculate_traffic_reduction(caching):
    cached = caching.query('source == "cache"')
    total = caching.shape[0]
    return cached.shape[0] / total


def calculate_ttl(estimator):
    # TODO: Have estimator output TTL
    experiment_id = sys.argv[1].split('/')[-1]
    ttl = experiment_id.split('-')[0]
    return int(ttl)


def main(experiment):
    client = pd.read_csv(experiment + '/client.log')
    caching = pd.read_csv(experiment + '/caching.csv')
    estimator = pd.read_csv(experiment + '/estimator.csv')
    server = pd.read_csv(experiment + '/server.log')

    error_fraction = calculate_error_fraction(client)
    traffic_reduction = calculate_traffic_reduction(caching)
    # TODO Only once we actually output this from estimator
    # ttl = calculate_ttl(estimator)
    #print('{},{},{}'.format(error_fraction, traffic_reduction, ttl))
    print('{},{}'.format(error_fraction, traffic_reduction)) # FIXME Should have TTL here


if __name__=="__main__":
    main(sys.argv[1])