import os
import json
import boto3

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import SQSEvent

STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

logger = Logger()
tracer = Tracer()

stepfunctions = boto3.client("stepfunctions")


@tracer.capture_lambda_handler
def lambda_handler(event: SQSEvent, context: LambdaContext):
    records = event["Records"]
    for record in records:
        body = json.loads(record["body"])

        bucket = body["Records"][0]["s3"]["bucket"]["name"]
        key = body["Records"][0]["s3"]["object"]["key"]

        stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({"bucket": bucket, "key": key}),
        )

    return {"message": "Step Function execution started", "bucket": bucket, "key": key}
