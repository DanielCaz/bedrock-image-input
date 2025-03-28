from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext):
    logger.info("Lambda invoked")

    return {"message": "Hello from Lambda!"}
