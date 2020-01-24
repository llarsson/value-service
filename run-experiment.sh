#!/bin/bash

set -x
set -euo pipefail

experiment_id=$1

duration=300
warmup=5

output_dir=$(pwd)/experiments/${experiment_id}
mkdir -p ${output_dir}

run_server () {
	docker run --name server -d --net host -e PORT=1100 value-service-server
}

run_estimator() {
	touch ${output_dir}/estimator.csv
	docker run --name estimator -d --net host -e PROXY_LISTEN_PORT=1110 -e VALUE_SERVICE_ADDR=localhost:1100 -e PROXY_MAX_AGE=20 -e PROXY_CACHE_BLACKLIST=.*Set.* -v ${output_dir}/estimator.csv:/app/data.csv value-service-estimator
}

run_cache() {
	touch ${output_dir}/caching.csv
	docker run --name caching -d --net host -e PROXY_LISTEN_PORT=1120 -e VALUE_SERVICE_ADDR=localhost:1110 -v ${output_dir}/caching.csv:/app/data.csv value-service-caching
}

run_client () {
	docker run --name client -d --net host -e VALUE_SERVICE_ADDR=localhost:1120 -e SEED=42 -e MEAN=20 -e COUNT=30 value-service-client
}

run_server
run_estimator
run_cache
echo "Sleeping for ${warmup} seconds..."
sleep ${warmup}
run_client

while docker ps | grep client; do
	echo "Client seems to be running still..."
	sleep 5
done

for component in client server estimator caching; do
	docker logs ${component} 2> ${output_dir}/${component}.log
	docker rm -f ${component}
done
