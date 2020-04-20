#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

import sys

def scatterplot(summary):
    no_cache = summary.query('name == "static" and parameter == 0')
    static = summary.query('name == "static" and parameter != 0')
    adaptive = summary.query('name == "dynamic-adaptive"')
    updaterisk = summary.query('name == "dynamic-updaterisk"')

    plt.scatter(static['error_fraction'], static['traffic_reduction'], marker='x', label='static')
    plt.scatter(adaptive['error_fraction'], adaptive['traffic_reduction'], marker='o', label='dynamic-adaptive')
    plt.scatter(updaterisk['error_fraction'], updaterisk['traffic_reduction'], marker='.', label='dynamic-updaterisk')

    plt.xlabel('Error fraction')
    plt.ylabel('Traffic reduction')
    plt.legend()

    plt.show()

if __name__=='__main__':
    summary = sys.argv[1]
    scatterplot(pd.read_csv(summary))
