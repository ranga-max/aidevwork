#!/bin/bash
docker exec spark-iceberg-master  nohup jupyter notebook --ip=0.0.0.0 --port=8443 --notebook-dir=/home/iceberg/notebooks --no-browser --allow-root --NotebookApp.keyfile=/root/.jupyter/server.key --NotebookApp.certfile=/root/.jupyter/server.crt --NotebookApp.token='' &> /dev/null &

