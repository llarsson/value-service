#!/bin/bash

# not -e this time!
set -uo pipefail

for repetition in $(seq 3); do
	echo "get_rate,set_rate,proxy_max_age,error_fraction,traffic_reduction,server_work_fraction,mean_ttl,median_ttl,mean_response_time" > experiments/${repetition}.csv
	for proxy_max_age in static-0 static-1 static-10 static-30 dynamic-simplistic dynamic-tbg1 dynamic-nyqvistish; do
		for get_rate in 100 50 10 5 1 0.2; do
			for set_rate in 0.01 0.02 0.1 0.2 1 5 10; do

				experiment_id="${proxy_max_age}-maxage-${get_rate}-getrate-${set_rate}-setrate-${repetition}-repetition"

				if [ -d experiments/${experiment_id} ]; then
					stats=$(./stats.py experiments/${experiment_id})
					if [ $? != 0 ]; then
						continue
					fi
					echo "${get_rate},${set_rate},${proxy_max_age},${stats}" >> experiments/${repetition}.csv || true
				fi

			done
		done
	done
done

