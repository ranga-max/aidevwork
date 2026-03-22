#kind load docker-image -n my-kind-cluster-east --nodes my-kind-cluster-east-worker2,my-kind-cluster-east-worker,my-kind-cluster-east-control-plane rrchak/cpflinklocal -v 3
#docker save rrchak/cpflinklocal -o cpflinklocal.tar
#kind load image-archive cpflinklocal.tar
#kind load image-archive cpflinklocal.tar -n my-kind-cluster-east --nodes my-kind-cluster-east-worker2,my-kind-cluster-east-worker,my-kind-cluster-east-control-plane
#docker save rrchak/hms -o hms.tar
#kind load image-archive hms.tar -n my-kind-cluster-east --nodes my-kind-cluster-east-worker2,my-kind-cluster-east-worker,my-kind-cluster-east-control-plane
#docker exec -it my-kind-cluster-east-control-plane crictl images
kubectl delete -f jm.yaml
kubectl apply -f jm.yaml
kubectl delete -f jms.yaml
kubectl apply -f jms.yaml
kubectl delete -f tm.yaml
kubectl apply -f tm.yaml
kubectl delete -f sc.yaml
kubectl apply -f sc.yaml
