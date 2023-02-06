```bash
{
  "churn": {
    "customer_age": 100,
    "gender": "F",
    "dependent_count": 2,
    "education_level": 2,
    "marital_status": "married",
    "income_category": 2,
    "card_category": "blue",
    "months_on_book": 6,
    "total_relationship_count": 3,
    "credit_limit": 4000,
    "total_revolving_bal": 2500
  },
  "churn_id": 123
}
```


```bash
KINESIS_STREAM_INPUT=churn-events
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data "Hello, this is a test."

```

```bash
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49637735388523780030213855657028824557748410478621622274",
                "data": "Hellothisisatest",
                "approximateArrivalTimestamp": 1675612577.107
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49637735388523780030213855657028824557748410478621622274",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::130391109865:role/kinesis-lambda-role-4",
            "awsRegion": "ap-south-1",
            "eventSourceARN": "arn:aws:kinesis:ap-south-1:130391109865:stream/churn-events"
        }
    ]
}
```

```bash
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --cli-binary-format raw-in-base64-out \
    --data '{
      "churn": {
        "customer_age": 100,
        "gender": "F",
        "dependent_count": 2,
        "education_level": 2,
        "marital_status": "married",
        "income_category": 2,
        "card_category": "blue",
        "months_on_book": 6,
        "total_relationship_count": 3,
        "credit_limit": 4000,
        "total_revolving_bal": 2500
      },
      "churn_id": 123
    }'
```


```bash
response = client.put_record(
    StreamName='string',
    Data=b'bytes',
    PartitionKey='string',
    ExplicitHashKey='string',
    SequenceNumberForOrdering='string',
    StreamARN='string'
)
```

### Reading from the stream

```bash
KINESIS_STREAM_OUTPUT='churn-prediction'
SHARD='shardId-000000000000'
SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)
```
##### then run one after another: 
###### before that install jq : pip install jq
```bash
RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode | jq

```

