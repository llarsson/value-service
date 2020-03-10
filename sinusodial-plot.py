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

def calculate_errors(client):
    client['difference'] = client['correct'] - client['actual']
    client['errors'] = client['difference'].clip(0,1)

def calculate_true_ttl(server):
    # query for when we have done a 'set' and do something with timestamp difference and clip?

    # column with nanoseconds since previous 'set'?

def main(experiment, bins):
    client = normalize_timestamps(pd.read_csv(experiment + '/client.log'))
    caching = normalize_timestamps(pd.read_csv(experiment + '/caching.csv'))
    estimator = normalize_timestamps(pd.read_csv(experiment + '/estimator.csv'))
    server = normalize_timestamps(pd.read_csv(experiment + '/server.log'))

    calculate_errors(client)
    calculate_true_ttl(server)

    binned_client = resample(client)
    binned_estimator = resample(estimator)
    binned_client['errors'].plot(kind='bar', color='red', label='Mean error fraction')
    binned_estimator['estimate'].plot(kind='bar', color='green', label='Mean estimated TTL')

    plt.legend()
    plt.show()

if __name__=='__main__':
    main(sys.argv[1], 30)
    sys.exit(0)
