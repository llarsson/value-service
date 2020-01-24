#!/bin/bash

set -euo pipefail

for repetition in $(seq 3); do
	for proxy_max_age in 0 1 10 30 dynamic; do
		for get_rate in 1 2 3 4 5 6 7 8 9 10; do
			for set_rate in 1 2 3 4 5 6 7 8 9 10; do
				experiment_id="${proxy_max_age}-maxage-${get_rate}-getrate-${set_rate}-setrate-${repetition}-repetition"
				echo "${experiment_id}"
				./run-experiment.sh ${experiment_id} ${get_rate} ${set_rate} ${proxy_max_age}
			done
		done
	done
done
