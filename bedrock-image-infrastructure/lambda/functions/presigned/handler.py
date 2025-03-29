import os
import boto3

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    CORSConfig,
    Response,
    content_types,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

CORS_URL = os.environ.get("CORS_URL", "*")
BUCKET_NAME = os.environ["BUCKET_NAME"]

logger = Logger()
tracer = Tracer()
cors_config = CORSConfig(allow_origin=CORS_URL)

app = APIGatewayRestResolver(cors=cors_config)

s3 = boto3.client("s3")


@app.post("/presigned")
def main():
    response = s3.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key="${filename}",
        Fields={
            "Content-Type": "application/pdf",
            "success_action_status": "201",
        },
        Conditions=[
            {"Content-Type": "application/pdf"},
            {"success_action_status": "201"},
        ],
    )

    return {
        "message": "Presigned URL generated successfully",
        "url": response["url"],
        "fields": response["fields"],
    }


@app.exception_handler(Exception)
def handle_exception(e: Exception):
    logger.exception(f"An unexpected error occurred: {e}")

    return Response(
        status_code=500,
        content_type=content_types.APPLICATION_JSON,
        body={"message": "An unexpected error occurred", "error": str(e)},
    )


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)
