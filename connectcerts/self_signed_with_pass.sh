#openssl genrsa -aes256 -passout pass:test -out rootca.key 2048 
#openssl genrsa -passout pass:test -out rootca.key 2048
openssl genrsa -out rootca.key 4096
#openssl req -new -x509 -key rootca.key -sha256 -days 3650 -out rootca.crt -subj "/CN=TESTCA"
openssl req -new -x509 -key rootca.key -days 3650 -out rootca.crt -subj "/CN=TESTCA"
#openssl req -new -x509 -keyout ca.key -out ca.crt -days 3650 -subj '/CN=TESTCA/O=CONFLUENT/L=Jersey City/S=New Jersey/C=US' -passin pass:confluent -passout pass:confluent
#openssl genrsa -passout pass:test  -out server.key 2048
openssl genrsa -out server.key 4096
#openssl genrsa -aes256 -passout pass:test -out server_key.pem 2048
#openssl rsa -in server.key -out server_key.pem -outform PEM -passin pass:test -passout pass:test 
#openssl req -new -key server.key -out server.csr -subj "/CN=connect" -passin pass:test
#openssl req -new -key server_key.pem -out server.csr -subj "/CN=connect" -passin pass:test
openssl req -new -key server.key -out server.csr -subj "/CN=connect"
#openssl x509 -req -in server.csr -CA rootca.pem -CAkey rootca.key -CAcreateserial -out server.pem -days 365 -sha256 -passin pass:test
openssl x509 -req -in server.csr -CA rootca.crt -CAkey rootca.key -CAcreateserial -out server.crt -days 365
openssl verify -verbose -CAfile rootca.crt  server.crt

openssl pkcs12 -export -in server.crt -inkey server.key -chain -CAfile rootca.crt -name connect -out connect.p12

keytool -importkeystore -srckeystore connect.p12 -srcstorepass confluent -srcstoretype pkcs12 -destkeystore kafka.keystore.pkcs12 -deststoretype pkcs12 -deststorepass confluent -noprompt 
keytool -list -keystore kafka.keystore.pkcs12 -storepass confluent
keytool -keystore kafka.truststore.jks -alias CARoot -import -file rootca.crt -storetype jks  -v -trustcacerts -storepass confluent -noprompt
keytool -importkeystore -srckeystore kafka.keystore.pkcs12  -srcstoretype pkcs12 -srcstorepass confluent -srcalias connect -destkeystore kafka.keystore.jks -deststoretype jks -deststorepass confluent -destalias connect-jks
keytool -import -alias CAroot -file rootca.crt -trustcacerts -keystore kafka.keystore.jks -storepass confluent -noprompt
keytool -list -keystore kafka.keystore.jks -storepass confluent
keytool -export -alias caroot -keystore kafka.truststore.jks -file trust-ca.der
openssl x509 -inform der -in trust-ca.der -out trust-ca.pem


