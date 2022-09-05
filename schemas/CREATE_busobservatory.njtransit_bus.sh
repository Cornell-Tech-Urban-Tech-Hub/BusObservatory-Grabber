# needed because Glue crawler creates duplicate columns when crawling s3://busobservatory/

aws glue create-table \
--database-name=busobservatory \
--table-input='
{
        "Name": "njtransit_bus",
        "Retention": 0,
        "StorageDescriptor": {
            "Columns": [
                {
                    "Name": "id",
                    "Type": "string"
                },
                {
                    "Name": "consist",
                    "Type": "string"
                },
                {
                    "Name": "cars",
                    "Type": "string"
                },
                {
                    "Name": "m",
                    "Type": "string"
                },
                {
                    "Name": "rt",
                    "Type": "string"
                },
                {
                    "Name": "rtdd",
                    "Type": "string"
                },
                {
                    "Name": "c",
                    "Type": "string"
                },
                {
                    "Name": "d",
                    "Type": "string"
                },
                {
                    "Name": "dd",
                    "Type": "string"
                },
                {
                    "Name": "dn",
                    "Type": "string"
                },
                {
                    "Name": "lat",
                    "Type": "double"
                },
                {
                    "Name": "lon",
                    "Type": "double"
                },
                {
                    "Name": "pid",
                    "Type": "string"
                },
                {
                    "Name": "pd",
                    "Type": "string"
                },
                {
                    "Name": "run",
                    "Type": "string"
                },
                {
                    "Name": "fs",
                    "Type": "string"
                },
                {
                    "Name": "op",
                    "Type": "string"
                },
                {
                    "Name": "bid",
                    "Type": "string"
                },
                {
                    "Name": "wid1",
                    "Type": "string"
                },
                {
                    "Name": "wid2",
                    "Type": "string"
                },
                {
                    "Name": "timestamp",
                    "Type": "timestamp"
                },
                {
                    "Name": "rtpifeedname",
                    "Type": "string"
                },
                {
                    "Name": "rtrtpifeedname",
                    "Type": "string"
                },
                {
                    "Name": "pdrtpifeedname",
                    "Type": "string"
                }
            ],
            "Location": "s3://busobservatory/lake/njtransit_bus/",
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "Compressed": false,
            "NumberOfBuckets": -1,
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                "Parameters": {
                    "serialization.format": "1"
                }
            },
            "BucketColumns": [],
            "SortColumns": [],
            "Parameters": {
                "CrawlerSchemaDeserializerVersion": "1.0",
                "CrawlerSchemaSerializerVersion": "1.0",
                "UPDATED_BY_CRAWLER": "BusObservatory_All",
                "averageRecordSize": "29",
                "classification": "parquet",
                "compressionType": "none",
                "objectCount": "4288",
                "recordCount": "343657984",
                "sizeKey": "7135892313",
                "typeOfData": "file"
            },
            "StoredAsSubDirectories": false
        },
        "TableType": "EXTERNAL_TABLE",
        "Parameters": {
            "CrawlerSchemaDeserializerVersion": "1.0",
            "CrawlerSchemaSerializerVersion": "1.0",
            "UPDATED_BY_CRAWLER": "BusObservatory_All",
            "averageRecordSize": "29",
            "classification": "parquet",
            "compressionType": "none",
            "objectCount": "4288",
            "recordCount": "343657984",
            "sizeKey": "7135892313",
            "typeOfData": "file"
        }
    }
'
