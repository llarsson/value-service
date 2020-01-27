#!/usr/bin/env python3

import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('experiments/2.csv')



axes = plt.subplots(2,2)


plt.subplot(221)
plt.suptitle('Error fraction')
plt.title('TTL=0')
sns.heatmap(df.query('ttl == 0').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1, annot=True)
plt.subplot(222)
plt.title('TTL=1')
sns.heatmap(df.query('ttl == 1').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
plt.subplot(223)
plt.title('TTL=10')
sns.heatmap(df.query('ttl == 10').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)
plt.subplot(224)
plt.title('TTL=30')
sns.heatmap(df.query('ttl == 30').pivot(index='get_rate', columns='set_rate', values='error_fraction'), vmin=0, vmax=1,annot=True)

plt.show()
