#! /bin/bash

if [ "$#" -ne 2 ]
then
  echo "Error: No domain name argument provided"
  echo "Usage: Provide a domain name as an argument"
  exit 1
fi

DOMAIN=$1
GENCA=$2

#openssl req -new -key ca-key.pem -x509 \
#  -days 1000 \
#  -out ca.pem \
#  -subj "/C=US/ST=CA/L=MountainView/O=Confluent/OU=Operator/CN=TestCA"

# 1. Generate CA's private key and self-signed certificate
#openssl genrsa -aes256 -passout pass:confluent -out ca-key.pem 4096
#openssl req -x509 -new -key ca-key.pem -passin pass:confluent -out ca-cert.pem -nodes -subj "/C=US/ST=CA/L=MountainView/O=Confluent/OU=Operator/CN=TestCA"
#Generate Root Authority Certificate once and reuse it for all components
if [ "$GENCA" = "true" ]
then	
echo "command1"
openssl req -x509 -newkey rsa:4096 -days 365 -keyout ca-key.pem -out ca-cert.pem -nodes -subj "/C=US/ST=CA/L=MountainView/O=Confluent/OU=Operator/CN=TestCA"
fi

# Generate web server's private key and CSR
echo "command2"
openssl genrsa -aes256 -passout pass:confluent -out ${DOMAIN}-key.pem 4096
echo "command3"
openssl req -new -key ${DOMAIN}-key.pem -passin pass:confluent -out ${DOMAIN}-req.csr -nodes -subj "/C=US/ST=CA/L=MountainView/O=Confluent/OU=Operator/CN=connect"

#openssl req -newkey rsa:4096 -keyout ${DOMAIN}-key.pem -passout pass:confluent -out ${DOMAIN}-req.csr -nodes -subj "/C=US/ST=CA/L=MountainView/O=Confluent/OU=Operator/CN=cluster1.my.domain"

# 3. Sign the web server's certificate request
##Default certificate validity
#openssl x509 -req -in server-req.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem

#openssl x509 -req -in server-req.csr -days 365 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem
#Ensure the hostname that presents the TLS certficate to the client is either present as a CN or SAN below

# 4. 
echo "command4"
cat > ${DOMAIN}-ext.cnf << EOF

subjectAltName=DNS:*.my.domain,DNS:kafka.my.domain,DNS:*.rrchakdc1.ans.test.io,IP:172.192.0.1

EOF

echo"command5"
openssl x509 -req -in ${DOMAIN}-req.csr -days 365 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out ${DOMAIN}-cert.pem -extfile ${DOMAIN}-ext.cnf
#openssl x509 -req -in server-req.csr -days 365 -CA ca-cert.pem -CAkey ca-key.pem -passin pass:confluent -CAcreateserial -out server-cert.pem -extfile server-ext.cnf


#openssl x509 -req -in server-req.csr -days 365 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -ext "subjectAltName=DNS:*.my.domain,DNS:kafka.my.domain,IP:172.192.0.1" 

echo "command6"
openssl pkcs12 -export \
    -in ${DOMAIN}-cert.pem \
    -inkey ${DOMAIN}-key.pem \
    -passin pass:confluent \
    -chain \
    -CAfile ca-cert.pem \
    -name ${DOMAIN} \
    -out ${DOMAIN}.p12 \
    -password pass:confluent

echo "command7"    
sudo keytool -importkeystore \
    -deststorepass confluent \
    -destkeypass confluent \
    -destkeystore ${DOMAIN}.keystore.pkcs12 \
    -srckeystore ${DOMAIN}.p12 \
    -deststoretype PKCS12  \
    -srcstoretype PKCS12 \
    -noprompt \
    -srcstorepass confluent

echo "command8"
keytool -list -v \
    -keystore ${DOMAIN}.keystore.pkcs12 \
    -storepass confluent

echo "command9"
keytool -importkeystore -srckeystore ${DOMAIN}.keystore.pkcs12 -srcstoretype pkcs12 \
 -srcalias ${DOMAIN} -srcstorepass confluent -srckeypass confluent -destkeystore ${DOMAIN}.keystore.jks \
 -deststoretype jks -deststorepass confluent -destkeypass confluent -destalias ${DOMAIN}-jks

echo "command10"
keytool -import -alias CAroot -file ca-cert.pem   -trustcacerts -keystore ${DOMAIN}.keystore.jks -storepass confluent -noprompt

echo "command11"
sudo keytool -keystore ${DOMAIN}.truststore.jks \
    -alias CARoot \
    -import \
    -v -trustcacerts \
    -file ca-cert.pem \
    -storepass confluent  \
    -noprompt \
    -storetype JKS

echo "command12"
keytool -list -v \
    -keystore ${DOMAIN}.keystore.jks \
    -storepass confluent

rm -f *.cnf *.csr *.srl 
#rm *.*12
