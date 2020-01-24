#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import sys

df = pd.read_csv(sys.argv[1] + '/client.log')

df['timestamp'] = df['timestamp'] - df['timestamp'][0]

plt.plot(df['timestamp'], df['correct'], label='correct')
plt.plot(df['timestamp'], df['actual'], label='actual')

df['difference'] = df['correct'] - df['actual']
plt.plot(df['timestamp'], df['difference'], label='difference')

plt.legend()
plt.show()

df['errors'] = df['difference'].clip(0,1)
error_count = df['errors'].sum()
error_fraction = df['errors'].sum() / df.size * 1.0

server = pd.read_csv(sys.argv[1] + '/server.log')
server_requests = server.query('operation == "get"').size

print("Total GET requests from client: {}".format(df.size))
print("GET requests handled by server: {} ({}% of total)".format(server_requests, (server_requests / df.size) * 100))
print("Error count: {}".format(error_count))
print("Error fraction: {}%".format(error_fraction * 100))
