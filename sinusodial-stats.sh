#!/bin/bash

set -euo pipefail

experiments_directory=${experiments_directory:-experiments}

for proxy_max_age in static-0 static-1 static-10 static-30 dynamic-adaptive-0.10 dynamic-adaptive-0.25 dynamic-adaptive-0.50 dynamic-updaterisk-0.10 dynamic-updaterisk-0.25 dynamic-updaterisk-0.50 dynamic-updaterisk-0.75 dynamic-updaterisk-0.90; do
	for setter_phase in 0 450 900 1800 ; do
		experiments=""
		for repetition in $(seq 3); do
		 	experiments+="${experiments_directory}/${proxy_max_age}-maxage-${setter_phase}-setter_phase-${repetition}-repetition "
		done
		experiment="${proxy_max_age}-${setter_phase}"
		./binned_stats.py ${experiments} > ${experiments_directory}/${experiment}_binned_stats.csv
		./averages.py ${proxy_max_age} ${setter_phase} ${experiments} > ${experiments_directory}/${experiment}_averages.csv
	done
done

./collect_averages.py ${experiments_directory} > ${experiments_directory}/summary.csv
