#!/usr/bin/env python3

import glob 
import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys

path = 'experiments'

if len(sys.argv) == 2:
    path = sys.argv[1]

sources = []
for file in glob.glob('{}/*.csv'.format(path)):
    sources.append( pd.read_csv(file) )
df = pd.concat(sources).groupby(['get_rate','set_rate','proxy_max_age']).mean().reset_index()

proxy_max_ages = ["static-0", "static-1", "static-10", "static-30", "dynamic-simplistic", "dynamic-tbg1", "dynamic-nyqvistish"]
keys = ['traffic_reduction', 'server_work_fraction', 'error_fraction', 'goodness']

titles = {
    'traffic_reduction': "Traffic reduction",
    'server_work_fraction': 'Server work fraction',
    'error_fraction': 'Error fraction',
    'goodness': 'Overall utility score'
}

alpha = np.log(2)
beta = np.log(2)
gamma = 2

#df['tr_over_err'] = np.power(df['traffic_reduction'], 1/beta) * (1 - np.power(df['error_fraction'], 1/alpha))
df['goodness'] = np.exp(alpha * (df['traffic_reduction'] - 1.0)) * np.exp(-beta * df['server_work_fraction']) * (1.0 - np.power(df['error_fraction'], 1.0/gamma))

def plot_static(key, vmin=0, vmax=1):
    static = [p for p in proxy_max_ages if "static" in p]
    fig, axes = plt.subplots(2, 2)
    axes = axes.reshape(-1)
    fig.suptitle(titles[key] + " (static TTL)")
    for (index, proxy_max_age) in enumerate(static):
        ax = axes[index]
        ax.set_title(proxy_max_age)
        sns.heatmap(df.query('proxy_max_age == "{}"'.format(proxy_max_age)).pivot(index='get_rate', columns='set_rate', values=key).round(2), vmin=vmin, vmax=vmax, annot=True, ax=ax)
        ax.invert_yaxis()

def plot_dynamic(key, vmin=0, vmax=1):
    dynamic = [p for p in proxy_max_ages if "dynamic" in p]
    fig, axes = plt.subplots(len(dynamic), 2)
    fig.suptitle(titles[key] + " (dynamically estimated TTL)")
    for (index, strategy) in enumerate(dynamic):
        relevant = df.query('proxy_max_age == "{}"'.format(strategy))

        ax = axes[index, 0]
        ax.set_title(strategy)
        sns.heatmap(relevant.pivot(index='get_rate', columns='set_rate', values=key).round(2), 
            vmin=vmin, vmax=vmax, annot=True, ax=ax)
        ax.invert_yaxis()

        ax = axes[index, 1]
        ax.set_title("Mean TTL for {}".format(strategy))
        sns.heatmap(relevant.pivot(index='get_rate', columns='set_rate', values="mean_ttl").round(2), 
            vmin=0, vmax=df['mean_ttl'].max(), annot=True, ax=ax)
        ax.invert_yaxis()

for key in keys:
    plot_static(key)
    plot_dynamic(key)

plt.show()
