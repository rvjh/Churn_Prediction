import lambda_function_stream_kinesis

event = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49637735388523780030213855667901903379362669224806842370",
                "data": "ewogICAgICAiY2h1cm4iOiB7CiAgICAgICAgImN1c3RvbWVyX2FnZSI6IDEwMCwKICAgICAgICAiZ2VuZGVyIjogIkYiLAogICAgICAgICJkZXBlbmRlbnRfY291bnQiOiAyLAogICAgICAgICJlZHVjYXRpb25fbGV2ZWwiOiAyLAogICAgICAgICJtYXJpdGFsX3N0YXR1cyI6ICJtYXJyaWVkIiwKICAgICAgICAiaW5jb21lX2NhdGVnb3J5IjogMiwKICAgICAgICAiY2FyZF9jYXRlZ29yeSI6ICJibHVlIiwKICAgICAgICAibW9udGhzX29uX2Jvb2siOiA2LAogICAgICAgICJ0b3RhbF9yZWxhdGlvbnNoaXBfY291bnQiOiAzLAogICAgICAgICJjcmVkaXRfbGltaXQiOiA0MDAwLAogICAgICAgICJ0b3RhbF9yZXZvbHZpbmdfYmFsIjogMjUwMAogICAgICB9LAogICAgICAiY2h1cm5faWQiOiAxMjMKICAgIH0=",
                "approximateArrivalTimestamp": 1675616709.193
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49637735388523780030213855667901903379362669224806842370",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::130391109865:role/kinesis-lambda-role-4",
            "awsRegion": "ap-south-1",
            "eventSourceARN": "arn:aws:kinesis:ap-south-1:130391109865:stream/churn-events"
        }
    ]
}

result = lambda_function_stream_kinesis.lambda_handler(event,None)
print(result)
