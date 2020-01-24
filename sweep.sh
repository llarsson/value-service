#!/bin/bash

set -euo pipefail

for repetition in $(seq 3); do
	for proxy_max_age in 0 1 10 30 dynamic; do
		for get_rate in 100 50 10 5 1; do
			for set_rate in 0.01 0.02 0.1 0.2 1; do
				experiment_id="${proxy_max_age}-maxage-${get_rate}-getrate-${set_rate}-setrate-${repetition}-repetition"
				echo "${experiment_id}"
				./run-experiment.sh ${experiment_id} ${get_rate} ${set_rate} ${proxy_max_age}
			done
		done
	done
done
