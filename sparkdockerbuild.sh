./docker-image-tool.sh -u root -r rrchak-spark-iceberg -t latest -f /home/ubuntu/cpflink/spark-3.5.6-bin-hadoop3/kubernetes/dockerfiles/spark/Dockerfile build
./docker-image-tool.sh -u root -r rrchak-spark-iceberg-py -t latest -p /home/ubuntu/cpflink/spark-3.5.6-bin-hadoop3/kubernetes/dockerfiles/spark/bindings/python/Dockerfile build
docker build -t rrchak/sparkiceberg -f Dockerfile-spark-kafka .
docker push rrchak/sparkiceberg
