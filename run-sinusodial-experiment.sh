#!/bin/bash

set -euo pipefail

experiment_id=$1
proxy_max_age=$2
setter_phase=$2

duration=${duration:=600}
seed=${seed:=42}
warmup=5

output_dir=$(pwd)/experiments/${experiment_id}
network_id=value-${experiment_id}
mkdir -p ${output_dir}

run_server () {
	docker run --name server-${experiment_id} -d --net ${network_id} --network-alias=server -e PORT=1100 value-service-multiserver &> /dev/null
}

run_estimator() {
	touch ${output_dir}/estimator.csv
	docker run --name estimator-${experiment_id} -d --net ${network_id} --network-alias=estimator -e PROXY_LISTEN_PORT=1110 -e VALUE_SERVICE_ADDR=server:1100 -e PROXY_MAX_AGE=${proxy_max_age} -e PROXY_CACHE_BLACKLIST=.*Set.* -v ${output_dir}/estimator.csv:/app/data.csv value-service-estimator &> /dev/null
}

run_cache() {
	touch ${output_dir}/caching.csv
	docker run --name caching-${experiment_id} -d --net ${network_id} --network-alias=caching -e PROXY_LISTEN_PORT=1120 -e VALUE_SERVICE_ADDR=estimator:1110 -v ${output_dir}/caching.csv:/app/data.csv value-service-caching &> /dev/null
}

run_client () {
	touch ${output_dir}/client-getter-stats.txt
	touch ${output_dir}/client-setter-stats.txt
	docker run --name client-${experiment_id} -d --net ${network_id} --network-alias=client \
		-e VALUE_SERVICE_ADDR=caching:1120 \
		-e SEED=${seed} \
		-e GETTER_MODE=sinusodial \
		-e SETTER_MODE=sinusodial \
		-e DURATION=${duration} \
		-e GETTER_SINUSODIAL_MIN_RATE=1 \
		-e GETTER_SINUSODIAL_MAX_RATE=10 \
		-e GETTER_SINUSODIAL_PERIOD=${duration} \
		-e GETTER_SINUSODIAL_PHASE=0 \
		-e SETTER_SINUSODIAL_MIN_RATE=0.05 \
		-e SETTER_SINUSODIAL_MAX_RATE=1.1 \
		-e SETTER_SINUSODIAL_PERIOD=${duration} \
		-e SETTER_SINUSODIAL_PHASE=${setter_phase} \
		-v ${output_dir}/client-setter-stats.txt:/app/setter_stats.txt -v ${output_dir}/client-getter-stats.txt:/app/getter_stats.txt value-service-multiclient &> /dev/null
}

cleanup() {
	echo "Cleaning up..."
	for component in client server estimator caching; do
		docker rm -f ${component}-${experiment_id} &> /dev/null || true
	done
	docker network rm ${network_id} &> /dev/null || true
}

trap cleanup EXIT

cleanup

echo -n "${experiment_id} of duration ${duration} (seed ${seed}) started at "
date

docker network create ${network_id} &> /dev/null

run_server
run_estimator
run_cache
sleep ${warmup}
run_client

while docker ps | grep client > /dev/null; do
	echo -n "."
	sleep 5
done

echo ""
echo "Done! Storing logs..."
for component in client server estimator caching; do
	docker logs ${component}-${experiment_id} 2> ${output_dir}/${component}.log
done
