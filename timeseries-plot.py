#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

from binned_stats import binned_stats

def plot_rates(results, original_axis, plot_queries=True, plot_updates=True):
    rate_ax = original_axis.twinx()
    if plot_queries:
        rate_ax.plot('epoch_timestamp', 'mean_request_rate', '.-', data=results, label='Mean query rate (req/s)', color='#FFA50080')
    if plot_updates:
        rate_ax.plot('epoch_timestamp', 'mean_update_rate', '.-', data=results, label='Mean update rate (req/s)', color='#6A5ACD80')
    if plot_updates or plot_updates:
        rate_ax.legend(loc='center right')

def plot(experiment, results):
    # Actual plotting
    fig, axs = plt.subplots(5, 1, sharex=True)
    fig.suptitle(experiment)

    ttl_ax = axs[0]
    ttl_ax.step('epoch_timestamp', 'mean_estimated_ttl', data=results, label='Mean estimated TTL (s)')
    ttl_ax.step('epoch_timestamp', 'mean_true_ttl', data=results, label='Mean true TTL (s)')
    ttl_ax.legend(loc='upper left')
    plot_rates(results, ttl_ax, plot_queries=False)

    tr_ax = axs[1]
    #tr_ax.set_ylim(0.0, 1.0)
    tr_ax.step('epoch_timestamp', 'mean_traffic_reduction', data=results, label='Mean traffic reduction')
    tr_ax.legend(loc='upper left')
    plot_rates(results, tr_ax)

    ef_ax = axs[2]
    #ef_ax.set_ylim(0.0, 1.0)
    ef_ax.step('epoch_timestamp', 'mean_error_fraction', data=results, label='Mean error fraction')
    ef_ax.legend(loc='upper left')
    plot_rates(results, ef_ax)

    wf_ax = axs[3]
    #wf_ax.set_ylim(0.0, 1.5)
    wf_ax.step('epoch_timestamp', 'mean_work_fraction', data=results, label='Mean work fraction')
    wf_ax.legend(loc='upper left')
    plot_rates(results, wf_ax)

    g_ax = axs[4]
    g_ax.step('epoch_timestamp', 'mean_goodness', data=results, label='Mean goodness')
    #g_ax.set_ylim(0.0, 1.0)
    g_ax.legend(loc='upper left')
    plot_rates(results, g_ax)

    plt.show()

if __name__=='__main__':
    experiments = sys.argv[1:]

    if len(experiments) == 1 and '.csv' in experiments[0]:
        experiment = experiments[0]
        data = pd.read_csv(experiment)
        plot(experiment, data)
    else:
        sources = []

        for experiment in experiments:
            results = binned_stats(experiment, 60)
            if len(results) == 31:
                results.drop(results.tail(1).index, inplace=True)
            sources.append(results)

        averages = pd.concat(sources)
        averages = averages.groupby(averages.index).mean()

        plot(', '.join(experiments), averages)
