#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
from math import pi

import sys

def radar_chart(df, item=0):
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
    plt.xticks(angles[:-1], categories, color='grey', size=8)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([n / 10 for n in range(1, 12, 3)], color="grey", size=7)
    plt.ylim(0,1.2)
    # }}}

    # Pick data to plot
    element = None
    if isinstance(item, int):
        element=df.iloc[item]
    else:
        element=df.loc[item]

    # We need to repeat the first value to close the circular graph:
    values=element.values.flatten().tolist()
    values += values[:1]
    
    # Plot data
    ax.plot(angles, values, linewidth=1, linestyle='solid', label=element.name)
    ax.fill(angles, values, alpha=0.1)

    # FIXME make pretty
    plt.legend()#)loc='upper right')#, bbox_to_anchor=(0.1, 0.1))
    plt.show()

if __name__=='__main__':
    summary = pd.read_csv(sys.argv[1])
    summary.set_index(['algorithm', 'phase'], inplace=True)
    summary.drop('goodness', axis=1, inplace=True)
    print(summary.index)
    radar_chart(summary, ('dynamic-updaterisk-0.50', 900.0))

