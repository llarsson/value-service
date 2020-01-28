#!/usr/bin/env python3

import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('experiments/1.csv')

plt.figure(1)
plt.subplot(221)
plt.suptitle('Error fraction')
plt.title('TTL=0')
ax = sns.heatmap(df.query('proxy_max_age == 0').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1, annot=True)
ax.invert_yaxis()
plt.subplot(222)
plt.title('TTL=1')
ax = sns.heatmap(df.query('proxy_max_age == 1').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
ax.invert_yaxis()
plt.subplot(223)
plt.title('TTL=10')
ax = sns.heatmap(df.query('proxy_max_age == 10').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
ax.invert_yaxis()
plt.subplot(224)
plt.title('TTL=30')
ax = sns.heatmap(df.query('proxy_max_age == 30').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
ax.invert_yaxis()


plt.figure(2)
plt.subplot(221)
plt.suptitle('Traffic reduction')
plt.title('TTL=0')
ax = sns.heatmap(df.query('proxy_max_age == 0').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1, annot=True)
ax.invert_yaxis()
plt.subplot(222)
plt.title('TTL=1')
ax = sns.heatmap(df.query('proxy_max_age == 1').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1,annot=True)
ax.invert_yaxis()
plt.subplot(223)
plt.title('TTL=10')
ax = sns.heatmap(df.query('proxy_max_age == 10').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1,annot=True)
ax.invert_yaxis()
plt.subplot(224)
plt.title('TTL=30')
ax = sns.heatmap(df.query('proxy_max_age == 30').pivot(index='get_rate', columns='set_rate', values='traffic_reduction'), vmin=0, vmax=1,annot=True)
ax.invert_yaxis()


alpha = 2
beta = 1
df['tr_over_err'] = np.power(df['traffic_reduction'], 1/beta) * (1 - np.power(df['error_fraction'], 1/alpha))

plt.figure(3)
plt.subplot(221)
plt.suptitle('Traffic reduction over error fraction')
plt.title('TTL=0')
ax = sns.heatmap(df.query('proxy_max_age == 0').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
ax.invert_yaxis()
plt.subplot(222)
plt.title('TTL=1')
ax = sns.heatmap(df.query('proxy_max_age == 1').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
ax.invert_yaxis()
plt.subplot(223)
plt.title('TTL=10')
ax = sns.heatmap(df.query('proxy_max_age == 10').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
ax.invert_yaxis()
plt.subplot(224)
plt.title('TTL=30')
ax = sns.heatmap(df.query('proxy_max_age == 30').pivot(index='get_rate', columns='set_rate', values='tr_over_err'), vmin=0, vmax=1, annot=True)
ax.invert_yaxis()

plt.show()
