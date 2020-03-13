#!/bin/bash

# Not -e, so we have to handle errors ourselves
set -uo pipefail

sweepfile=sweep.joblist

rm ${sweepfile} || true

for repetition in $(seq 3); do
	for proxy_max_age in static-0 static-1 static-10 static-30 dynamic-adaptive-0.1 dynamic-adaptive-0.25 dynamic-adaptive-0.5 dynamic-updaterisk-0.1 dynamic-updaterisk-0.25 dynamic-updaterisk-0.50 dynamic-updaterisk-0.75 dynamic-updaterisk-0.90; do
		for setter_phase in -5454.5 450 900 1800 ; do
		 	experiment_id="${proxy_max_age}-maxage-${setter_phase}-setter_phase-${repetition}-repetition"
		 	export duration=1800
		 	export seed=${repetition}
		 	echo "duration=${duration} seed=${seed} ./run-sinusodial-experiment.sh ${experiment_id} ${proxy_max_age} ${setter_phase}" >> ${sweepfile}
		done
	done
done

echo "Now run: parallel --jobs 5 < ${sweepfile}"
