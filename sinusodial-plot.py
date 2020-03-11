#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

def normalize_timestamps(df):
    df['timestamp'] = df['timestamp'] - df['timestamp'][0]
    return df

def resample(df, period='60s'):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
    df.set_index('timestamp', drop=False, inplace=True)
    return df.resample(period).mean()

def resample_sum(df, period='60s'):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
    df.set_index('timestamp', drop=False, inplace=True)
    return df.resample(period).sum()

def calculate_errors(client):
    client['difference'] = client['correct'] - client['actual']
    client['errors'] = client['difference'].clip(0,1)

def calculate_request_rate(client):
    return client.assign(gets_from_client=lambda x: 1)

def calculate_update_rate(server):
    sets_at_server = server.query('operation == "set"')
    return sets_at_server.assign(update=lambda x: 1)

def calculate_true_ttl(server):
    # query for when we have done a 'set' and do something with timestamp difference and clip?

    # column with nanoseconds since previous 'set'?

    # give me all 'set'
    # pandas 'diff' on timestamp column gives how long a value was valid
    sets_at_server = server.query('operation == "set"')
    sets_at_server = sets_at_server.drop(columns=['operation', 'value']).rename(columns={'timestamp': 'actual_ttl'}).diff()

    sets_at_server['actual_ttl'] = sets_at_server['actual_ttl'] / 1000000000.0 # ns to second conversion


    return server.merge(sets_at_server, how='outer', right_index=True, left_index=True)

def calculate_traffic_reduction(caching):
    gets = caching.query('method == "/ValueService/GetValue()"')
    return gets.assign(hit=lambda x: caching['source'] == 'cache')

def calculate_work_reduction(server, client, period='60s'):
    gets_at_server = server.query('operation == "get"').assign(gets_at_server=lambda x: 1)

    # note: client log only contains the "gets" in the first place
    gets_from_client = client.assign(gets_from_client=lambda x: 1)

    gets_at_server = gets_at_server.drop(columns=['operation', 'value'])
    gets_from_client = gets_from_client.drop(columns=['response_time', 'correct', 'actual', 'difference', 'errors'])

    work_reduction = gets_at_server.merge(gets_from_client, how='outer')
    return work_reduction

def calculate_goodness(binned_traffic_reduction, binned_work_reduction, binned_client):
    alpha = np.log(2)
    beta = np.log(2)
    gamma = 2
    return pd.DataFrame(data=np.exp(alpha * (binned_traffic_reduction['hit'] - 1.0)) * np.exp(-beta * binned_work_reduction['fraction']) * (1.0 - np.power(binned_client['errors'], 1.0/gamma)), columns=['mean_goodness'])

def binned_stats(experiment, period=60):
    client = normalize_timestamps(pd.read_csv(experiment + '/client.log'))
    caching = normalize_timestamps(pd.read_csv(experiment + '/caching.csv'))
    estimator = normalize_timestamps(pd.read_csv(experiment + '/estimator.csv'))
    server = normalize_timestamps(pd.read_csv(experiment + '/server.log'))

    calculate_errors(client)
    calculate_true_ttl(server)

    request_rate = calculate_request_rate(client)
    update_rate = calculate_update_rate(server)

    traffic_reduction = calculate_traffic_reduction(caching)

    true_ttl = calculate_true_ttl(server)
    binned_true_ttl = resample(true_ttl)

    work_reduction = calculate_work_reduction(server, client)
    binned_work_reduction = resample_sum(work_reduction, period='{}s'.format(period))
    binned_work_reduction['fraction'] = binned_work_reduction['gets_at_server'] / binned_work_reduction['gets_from_client']

    binned_client = resample(client, period='{}s'.format(period))
    binned_estimator = resample(estimator, period='{}s'.format(period))
    binned_traffic_reduction = resample(traffic_reduction, period='{}s'.format(period))

    binned_request_rate = resample_sum(request_rate, period='{}s'.format(period))
    binned_request_rate['rate'] = binned_request_rate['gets_from_client'] / float(period)

    binned_update_rate = resample_sum(update_rate, period='{}s'.format(period))
    binned_update_rate['rate'] = binned_update_rate['update'] / float(period)

    binned_goodness = calculate_goodness(binned_traffic_reduction, binned_work_reduction, binned_client)

    result = binned_goodness.copy(deep=True)
    result['mean_estimated_ttl'] = binned_estimator['estimate']
    result['mean_true_ttl'] = binned_true_ttl['actual_ttl']
    result['mean_request_rate'] = binned_request_rate['rate']
    result['mean_update_rate'] = binned_update_rate['rate']
    result['mean_traffic_reduction'] = binned_traffic_reduction['hit']
    result['mean_work_fraction'] = binned_work_reduction['fraction']
    result['mean_error_fraction'] = binned_client['errors']

    result['epoch_timestamp'] = result.index.astype('int64')

    return result

def plot(experiment, results):
    # Actual plotting
    fig, ax1 = plt.subplots()
    fig.suptitle(experiment)

    ax1.step('epoch_timestamp', 'mean_estimated_ttl', data=results, label='Mean estimated TTL (s)')
    ax1.step('epoch_timestamp', 'mean_true_ttl', data=results, label='Mean true TTL (s)')
    ax1.step('epoch_timestamp', 'mean_request_rate', data=results, label='Mean request rate (req/s)')
    ax1.step('epoch_timestamp', 'mean_update_rate', data=results, label='Mean update rate (req/s)')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.step('epoch_timestamp', 'mean_traffic_reduction', data=results, label='Mean traffic reduction')
    ax2.step('epoch_timestamp', 'mean_error_fraction', data=results, label='Mean error fraction')
    ax2.step('epoch_timestamp', 'mean_work_fraction', data=results, label='Mean work fraction')
    ax2.step('epoch_timestamp', 'mean_goodness', data=results, label='Mean goodness')
    ax2.legend(loc='upper right')

    plt.show()

if __name__=='__main__':
    experiment = sys.argv[1]
    results = binned_stats(experiment, 60)

    if len(results) == 31:
        results.drop(results.tail(1).index, inplace=True)

    plot(experiment, results)
    results.to_csv('{}/results.csv'.format(experiment))

