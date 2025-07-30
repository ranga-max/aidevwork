* Hive Catalog for Kafka*
CREATE CATALOG c_hive WITH (
        'type' = 'hive',
        'hive-conf-dir' = '/opt/flink/conf/');

USE CATALOG c_hive;


* Hive Catalog for Iceberg Tables*
CREATE CATALOG c_iceberg_hive WITH (
        'type'          = 'iceberg',
        'catalog-type'  = 'hive',
        'warehouse'     = 's3a://warehouse',
        'hive-conf-dir' = '/opt/flink/conf/');

use CATALOG c_iceberg_hive;

CREATE DATABASE `c_iceberg_hive`.`db_iceberg`;
USE `c_iceberg_hive`.`db_iceberg`;
CREATE TABLE t_foo (c1 varchar, c2 int);
INSERT INTO t_foo VALUES ('a', 42);

CREATE CATALOG c_iceberg_s3_hive WITH (
        'type'          = 'iceberg',
        'catalog-type'  = 'hive',
        'warehouse'     = 's3://rrchak-warehouse',
        'hive-conf-dir' = '/opt/flink/conf/');

use CATALOG c_iceberg_s3_hive;

CREATE CATALOG c_iceberg_rest WITH (
        'type'          = 'iceberg',
        'catalog-type'='rest',
        'uri'='http://rest:8181/‘);

CREATE CATALOG c_iceberg_rest WITH (
  'type'='iceberg',
  'catalog-type'='rest',
  'uri'='http://rest:8181',
   'warehouse'='s3a://warehouse',
  's3.access-key-id'='admin',
  's3.secret-access-key'='password',
  's3.endpoint'='http://localhost:9000'
);

##DELTA TABLE
*CATALOG FOR DELTA TABLE*
CREATE CATALOG c_delta
    WITH ('type'         = 'delta-catalog',
          'catalog-type' = 'in-memory');

CREATE DATABASE c_delta.db_new;

CREATE TABLE c_delta.db_new.t_foo (c1 VARCHAR,
                                   c2 INT)
    WITH ('connector'  = 'delta',
          'table-path' = 's3a://warehouse/');

INSERT INTO c_delta.db_new.t_foo
    VALUES ('a',42);

