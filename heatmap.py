#!/usr/bin/env python3

import glob 
import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sources = []

for file in glob.glob('experiments/*.csv'):
    sources.append( pd.read_csv(file) )

df = pd.concat(sources).groupby(['get_rate','set_rate','proxy_max_age']).mean().reset_index()

proxy_max_ages = [0, 1, 10, 30, "dynamic"]
keys = ['error_fraction', 'traffic_reduction', 'tr_over_err']

alpha = 2
beta = 1
df['tr_over_err'] = np.power(df['traffic_reduction'], 1/beta) * (1 - np.power(df['error_fraction'], 1/alpha))

def plot_values(key):
    fig, axes = plt.subplots(2, 3)
    axes = axes.reshape(-1)
    fig.suptitle(key)
    for (index, proxy_max_age) in enumerate(proxy_max_ages):
        ax = axes[index]
        ax.set_title('TTL={}'.format(proxy_max_age))
        sns.heatmap(df.query('proxy_max_age == "{}"'.format(proxy_max_age)).pivot(index='get_rate', columns='set_rate', values=key), vmin=0, vmax=1, annot=True, ax=ax)
        ax.invert_yaxis()
    ax = axes[5]
    ax.set_title('Mean TTL')
    sns.heatmap(df.query('proxy_max_age == "dynamic"').pivot(index='get_rate', columns='set_rate', values='mean_ttl'), annot=True, ax=ax)

for key in keys:
    plot_values(key)

plt.show()

 #
 #
 #
 #plt.figure(1)
 #plt.subplot(231)
 #plt.suptitle('Error fraction')
 #plt.title('TTL=0')
 #ax = sns.heatmap(df.query('proxy_max_age == 0').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1, annot=True)
 #ax.invert_yaxis()
 #plt.subplot(232)
 #plt.title('TTL=1')
 #ax = sns.heatmap(df.query('proxy_max_age == 1').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
 #ax.invert_yaxis()
 #plt.subplot(233)
 #plt.title('TTL=10')
 #ax = sns.heatmap(df.query('proxy_max_age == 10').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
 #ax.invert_yaxis()
 #plt.subplot(234)
 #plt.title('TTL=30')
 #ax = sns.heatmap(df.query('proxy_max_age == 30').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
 #ax.invert_yaxis()
 ## plt.subplot(235)
 ## plt.title('TTL=dynamic')
 ## ax = sns.heatmap(df.query('proxy_max_age == "dynamic"').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
 ## ax.invert_yaxis()
 #
 #
 #plt.figure(2)
 #plt.subplot(231)
 #plt.suptitle('Traffic reduction')
 #plt.title('TTL=0')
 #ax = sns.heatmap(df.query('proxy_max_age == 0').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1, annot=True)
 #ax.invert_yaxis()
 #plt.subplot(232)
 #plt.title('TTL=1')
 #ax = sns.heatmap(df.query('proxy_max_age == 1').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1,annot=True)
 #ax.invert_yaxis()
 #plt.subplot(233)
 #plt.title('TTL=10')
 #ax = sns.heatmap(df.query('proxy_max_age == 10').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1,annot=True)
 #ax.invert_yaxis()
 #plt.subplot(234)
 #plt.title('TTL=30')
 #ax = sns.heatmap(df.query('proxy_max_age == 30').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1,annot=True)
 #ax.invert_yaxis()
 ## plt.subplot(235)
 ## plt.title('TTL=dynamic')
 ## ax = sns.heatmap(df.query('proxy_max_age == "dynamic"').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1,annot=True)
 ## ax.invert_yaxis()
 #
 #
 #
 #plt.figure(3)
 #plt.subplot(231)
 #plt.suptitle('Traffic reduction over error fraction')
 #plt.title('TTL=0')
 #ax = sns.heatmap(df.query('proxy_max_age == 0').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
 #ax.invert_yaxis()
 #plt.subplot(232)
 #plt.title('TTL=1')
 #ax = sns.heatmap(df.query('proxy_max_age == 1').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
 #ax.invert_yaxis()
 #plt.subplot(233)
 #plt.title('TTL=10')
 #ax = sns.heatmap(df.query('proxy_max_age == 10').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
 #ax.invert_yaxis()
 #plt.subplot(234)
 #plt.title('TTL=30')
 #ax = sns.heatmap(df.query('proxy_max_age == 30').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
 #ax.invert_yaxis()
 ## plt.subplot(235)
 ## plt.title('TTL=dynamic')
 ## ax = sns.heatmap(df.query('proxy_max_age == "dynamic"').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
 ## ax.invert_yaxis()
 #
 #plt.show()
