#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import sys

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


def main(experiment, bins):
    client = normalize_timestamps(pd.read_csv(experiment + '/client.log'))
    caching = normalize_timestamps(pd.read_csv(experiment + '/caching.csv'))
    estimator = normalize_timestamps(pd.read_csv(experiment + '/estimator.csv'))
    server = normalize_timestamps(pd.read_csv(experiment + '/server.log'))

    calculate_errors(client)
    calculate_true_ttl(server)

    request_rate = calculate_request_rate(client)

    traffic_reduction = calculate_traffic_reduction(caching)

    true_ttl = calculate_true_ttl(server)
    binned_true_ttl = resample(true_ttl)

    work_reduction = calculate_work_reduction(server, client)
    binned_work_reduction = resample_sum(work_reduction)
    binned_work_reduction['fraction'] = binned_work_reduction['gets_at_server'] / binned_work_reduction['gets_from_client']

    binned_client = resample(client)
    binned_estimator = resample(estimator)
    binned_traffic_reduction = resample(traffic_reduction)

    binned_request_rate = resample_sum(request_rate)
    binned_request_rate['rate'] = binned_request_rate['gets_from_client'] / 60.0

    fix, ax1 = plt.subplots()

    binned_estimator['estimate'].plot(kind='bar', color='green', label='Mean estimated TTL (s)', ax=ax1)
    binned_true_ttl['actual_ttl'].plot(kind='bar', color='gray', label='Mean actual TTL (s)', ax=ax1)
    binned_request_rate['rate'].plot(kind='bar', color='black', label='Mean request rate (req/s)', ax=ax1)
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()

    binned_traffic_reduction['hit'].plot(kind='bar', color='blue', label='Mean cache hit ratio', ax=ax2)
    binned_client['errors'].plot(kind='bar', color='red', label='Mean error fraction', ax=ax2)
    binned_work_reduction['fraction'].plot(kind='bar', color='yellow', label='Mean work fraction', ax=ax2)

    ax2.legend(loc='upper right')

    plt.show()

if __name__=='__main__':
    main(sys.argv[1], 30)
    sys.exit(0)
