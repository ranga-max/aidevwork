docker exec -it my-kind-cluster-east-control-plane crictl images
docker exec -it my-kind-cluster-east-control-plane crictl rmi docker.io/rrchak/sparklocal
docker exec -it my-kind-cluster-east-worker crictl rmi docker.io/rrchak/sparklocal
docker exec -it my-kind-cluster-east-worker2 crictl rmi docker.io/rrchak/sparklocal
