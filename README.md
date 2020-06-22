# value-service

Simple gRPC service that exposes a single settable value. Used in "Towards soft circuit breaking in service meshes via caching using dynamically estimated TTLs".

## Running experiments

This repo has the code for the multi-threaded Server and multi-threaded Client. You will also need the [Cache](https://github.com/llarsson/value-service-caching) and [Estimator](https://github.com/llarsson/value-service-estimator). Get those, and make the Docker images for each component. They should have the following names:

 * `value-service-estimator`
 * `value-service-caching`
 * `value-service-multiserver` (`docker build -t value-service-multiserver -f Dockerfile.multi_server .` in this repo)
 * `value-service-multiclient` (`docker build -t value-service-multiclient -f Dockerfile.multi_client .` in this repo)

Define a new set of experiments using a script like `sinusodial-sweep.sh` in this repo, then run them using the command that the script outputs. Then, gather statistics using `sinusodial-stats.sh`. The resulting `summary.csv` file in your `experiments/` directory can then be plotted using, e.g., `scatterplot.py` (pass the file name as the script's parameter).
