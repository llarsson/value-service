#!/usr/bin/env python3

import pandas as pd
import glob
import sys

def collect_averages(directory):
    sources = []
    for csv_file in glob.glob('{}/*_averages.csv'.format(directory)):
        sources.append(pd.read_csv(csv_file))

    result = pd.concat(sources)
    result.set_index(['algorithm', 'phase'], inplace=True)
    return result

if __name__=='__main__':
    result = collect_averages(sys.argv[1])
    print(result.to_csv(None))
