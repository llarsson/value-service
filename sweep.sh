#!/bin/bash

# Not -e, so we have to handle errors ourselves
set -uo pipefail

sweepfile=sweep.joblist

rm ${sweepfile} || true

for repetition in $(seq 3); do
	for proxy_max_age in static-0 static-1 static-10 static-30 dynamic-simplistic dynamic-tbg1; do
		for get_rate in 100 50 25 10 5 1 0.2; do
			for set_rate in 0.01 0.02 0.04 0.1 0.2 1 5; do
				experiment_id="${proxy_max_age}-maxage-${get_rate}-getrate-${set_rate}-setrate-${repetition}-repetition"
				export duration=300
				export seed=${repetition}
				#until ./run-experiment.sh ${experiment_id} ${get_rate} ${set_rate} ${proxy_max_age}; do
				#	echo "Some error occurred, sleeping and trying again..."
				#	sleep 5
				#done
				echo "duration=${duration} seed=${seed} ./run-experiment.sh ${experiment_id} ${get_rate} ${set_rate} ${proxy_max_age}" >> ${sweepfile}
			done
		done
	done
done

echo "Now run: parallel --jobs 5 < ${sweepfile}"
