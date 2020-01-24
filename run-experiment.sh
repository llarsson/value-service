#!/bin/bash

set -euo pipefail

experiment_id=$1
get_rate=$2
set_rate=$3
proxy_max_age=$4

duration=600
warmup=5

output_dir=$(pwd)/experiments/${experiment_id}
mkdir -p ${output_dir}

run_server () {
	docker run --name server -d --net host -e PORT=1100 value-service-multiserver
}

run_estimator() {
	touch ${output_dir}/estimator.csv
	docker run --name estimator -d --net host -e PROXY_LISTEN_PORT=1110 -e VALUE_SERVICE_ADDR=localhost:1100 -e PROXY_MAX_AGE=${proxy_max_age} -e PROXY_CACHE_BLACKLIST=.*Set.* -v ${output_dir}/estimator.csv:/app/data.csv value-service-estimator
}

run_cache() {
	touch ${output_dir}/caching.csv
	docker run --name caching -d --net host -e PROXY_LISTEN_PORT=1120 -e VALUE_SERVICE_ADDR=localhost:1110 -v ${output_dir}/caching.csv:/app/data.csv value-service-caching
}

run_client () {
	touch ${output_dir}/client-getter-stats.txt
	touch ${output_dir}/client-setter-stats.txt
	docker run --name client -d --net host -e VALUE_SERVICE_ADDR=localhost:1120 -e SEED=42 -e GET_RATE=${get_rate} -e SET_RATE=${set_rate} -e DURATION=${duration} -v ${output_dir}/client-setter-stats.txt:/app/setter_stats.txt -v ${output_dir}/client-getter-stats.txt:/app/getter_stats.txt value-service-multiclient
}

run_server
run_estimator
run_cache
sleep ${warmup}
run_client

while docker ps | grep client > /dev/null; do
	echo -n "."
	sleep 5
done

for component in client server estimator caching; do
	docker logs ${component} 2> ${output_dir}/${component}.log
	docker rm -f ${component}
done
