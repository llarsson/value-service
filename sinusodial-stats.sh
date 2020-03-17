#!/bin/bash

set -euo pipefail

experiments_directory=${experiments_directory:-experiments}

for proxy_max_age in static-0 static-1 static-10 static-30 dynamic-adaptive-0.1 dynamic-adaptive-0.25 dynamic-adaptive-0.5 dynamic-updaterisk-0.1 dynamic-updaterisk-0.25 dynamic-updaterisk-0.50 dynamic-updaterisk-0.75 dynamic-updaterisk-0.90; do
	for setter_phase in -5454.5 450 900 1800 ; do
		experiments=""
		for repetition in $(seq 3); do
		 	experiments+="${experiments_directory}/${proxy_max_age}-maxage-${setter_phase}-setter_phase-${repetition}-repetition "
		done
		./binned_stats.py ${experiments} > ${experiments_directory}/${proxy_max_age}-${setter_phase}_binned_stats.csv
	done
done
