kubectl create namespace minio-tenant
kubectl kustomize github.com/minio/operator\?ref=v7.1.1 | kubectl apply -f -
