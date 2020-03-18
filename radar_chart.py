#!/usr/bin/env python3

# Thanks to https://python-graph-gallery.com/390-basic-radar-chart/

import matplotlib.pyplot as plt
import pandas as pd
from math import pi

import sys

category_labels = {'traffic_reduction': 'Traffic reduction',
        'server_work_fraction': 'Work fraction',
        'error_fraction': 'Error fraction'}

def radar_chart(df, indices, title=''):
    # configure axis {{{
    # number of variable
    categories=list(df.columns)
    N = len(categories)
    
    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)
    
    # Draw one axis per variable + add labels labels yet
    plt.xticks(angles[:-1], [category_labels[category] for category in categories], color='black', size=8)
    plt.tick_params(axis='x', pad=20)
    
    # Draw ylabels
    ax.set_rlim(0.0, 1.1)
    ax.set_rlabel_position(-60) # diagonally downward
    ax.set_rticks([0.0, 0.25, 0.5, 1.0], minor=['', '0.25', '0.50', '1.00'])
    # }}}

    for element in [df.loc[index] for index in indices]:
        # We need to repeat the first value to close the circular graph:
        values=element.values.flatten().tolist()
        values += values[:1]
        
        # Plot data
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=element.name)
        ax.fill(angles, values, alpha=0.1)

    plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15))
    plt.suptitle(title)
    plt.show()

def select_best(phase, key, ascending=True):
    nontrivial = summary.query('phase == "{}"'.format(phase)).drop(('static', 0.0, 1800.0))
    selection = (nontrivial.assign(rn=nontrivial.sort_values(key, ascending=ascending)
        .groupby('name').cumcount() + 1)
        .query('rn < 2'))
    selection.drop(['rn'], axis=1, inplace=True)
    return selection

if __name__=='__main__':
    summary = pd.read_csv(sys.argv[1])
    summary.set_index(['name', 'parameter', 'phase'], inplace=True)
    summary.drop('goodness', axis=1, inplace=True)

    #selection = select_best(1800, 'error_fraction')
    selection = summary.query('phase == 1800').query('name == "dynamic-adaptive"').sort_values('parameter')
    #selection = select_best(1800, ['server_work_fraction'], ascending=False)
    radar_chart(summary, selection.index, title='Behavior profile of Adaptive TTL (phase=1800)')

