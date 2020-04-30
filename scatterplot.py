#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

import sys

def scatterplot(summary):
    no_cache = summary.query('name == "static" and parameter == 0')
    static = summary.query('name == "static" and parameter != 0')
    adaptive = summary.query('name == "dynamic-adaptive"')
    updaterisk = summary.query('name == "dynamic-updaterisk"')

    plt.scatter(static['error_fraction'], static['traffic_reduction'], s=static['parameter'] / 30.0 * 200, marker='o',  label='static', facecolor='white', edgecolor='black', alpha=0.5)
    plt.scatter(adaptive['error_fraction'], adaptive['traffic_reduction'], s=adaptive['parameter'] / 0.5 * 200, marker='D',  label='dynamic-adaptive', facecolor='white', edgecolor='black', alpha=0.5)
    plt.scatter(updaterisk['error_fraction'], updaterisk['traffic_reduction'], s=updaterisk['parameter'] / 0.9 * 200, marker='s', label='dynamic-updaterisk', facecolor='white', edgecolor='black', alpha=0.5)

    plt.xlabel('Error fraction')
    plt.ylabel('Traffic reduction')
    plt.legend(loc='lower right')

    plt.grid(True)
    plt.tight_layout()

    plt.show()

if __name__=='__main__':
    summary = sys.argv[1]
    plt.rc('font', size=14)
    scatterplot(pd.read_csv(summary))
