openssl genrsa -out rootca.key 2048
openssl req -new -x509 -key rootca.key -sha256 -days 3650 -out rootca.pem -subj "/CN=TESTCA"
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=connect"
openssl x509 -req -in server.csr -CA rootca.pem -CAkey rootca.key -CAcreateserial -out connect.pem -days 365 -sha256




