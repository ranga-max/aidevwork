kubectl delete configmap rest-log4j2-cm
kubectl delete configmap hive-site-cm
kubectl delete configmap hive-site-iceberg-cm
kubectl create configmap rest-log4j2-cm --from-file=log4j2-properties=log4j2.xml
kubectl create configmap hive-site-cm --from-file=hive-site.xml=hive-site-hms-ovrd.xml
kubectl create configmap hive-site-iceberg-cm --from-file=hive-site.xml=hive-site-iceberg-ovrd.xml
kubectl create configmap spark-cm --from-file=spark-defaults.conf=spark-delta-defaults.conf
