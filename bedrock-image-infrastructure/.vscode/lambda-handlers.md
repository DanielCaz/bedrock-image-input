# Lambda Handlers

Lambda handlers must follow these guidelines:

1. Place handlers in the `lambda/functions/{function_name}/handler.py` file structure
2. Include an empty `__init__.py` file in each directory that contains a handler
3. Use the following template a lambda handler connected to an API Gateway:

```python
import os
# other imports

# Only import the libraries you need from Powertools
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    CORSConfig,
    Response,
    content_types,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

CORS_URL = os.environ.get("CORS_URL", "*")
# ENV_VAR = os.environ["ENV_VAR"]

logger = Logger()
tracer = Tracer()
cors_config = CORSConfig(allow_origin=CORS_URL)

app = APIGatewayRestResolver(cors=cors_config)

# service_name = boto3.client("service_name")


@app.{API_METHOD}("/{API_PATH}")
def main():
    # logic for the main function

    return {"message": "Hello from AWS Lambda!"} # Example response

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

```

4. Use the following template for a lambda handler not connected to an API Gateway:

```python
# Only import the libraries you need from Powertools
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

# ENV_VAR = os.environ["ENV_VAR"]

logger = Logger()
tracer = Tracer()

# service_name = boto3.client("service_name")

@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext):
    # logic for the main function

    return {"message": "Hello from Lambda!"} # Example response
```
