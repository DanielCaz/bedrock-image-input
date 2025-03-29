import os
import re
import json
import boto3
from base64 import b64encode
from urllib.parse import unquote_plus

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

MODEL_ID = os.environ["MODEL_ID"]

logger = Logger()
tracer = Tracer()

bedrock = boto3.client("bedrock-runtime")
s3 = boto3.client("s3")


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext):
    bucket = event["output"]["bucket"]
    folder = unquote_plus(event["output"]["folder"])

    logger.info(
        "Processing images from bucket", extra={"bucket": bucket, "folder": folder}
    )

    response_bedrock = call_bedrock(bucket, folder)

    response_bedrock_body = json.loads(response_bedrock["body"].read().decode("utf-8"))

    stop_reason = response_bedrock_body["stopReason"]
    if stop_reason != "end_turn":
        logger.error(f"Unexpected stop reason: {stop_reason}")

        raise Exception(f"Unexpected stop reason: {stop_reason}")

    json_response = format_ai_response(response_bedrock_body)

    return {
        "message": "Success",
        "ai_response": json_response,
    }


def call_bedrock(bucket: str, folder: str):
    images = get_images(bucket, folder)

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(
            {
                "system": [{"text": "You are a document analysis assistant."}],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            *images,
                            {
                                "text": """
                                Task:
                                Extract and analyze the content from the provided document images and return the information in a structured JSON format.

                                Context information:
                                - The input consists of one or more document images
                                - The images may contain text, tables, or other structured content
                                - The content should be processed sequentially if multiple pages are present
                                - Maintain the logical flow and hierarchy of the content

                                Model Instructions:
                                - Process each image thoroughly to extract all visible text
                                - Preserve the structure and relationships between different content elements
                                - Handle both typed and handwritten text if present
                                - Identify and properly format any tables, lists, or structured data
                                - Maintain proper paragraph breaks and section divisions

                                Response style and format requirements:
                                - Respond in the same language as the input
                                - Return the output as a valid JSON object
                                - Use appropriate nesting to represent document hierarchy
                                - Include a 'pages' array containing content from each page
                                - Output Schema:
                                {
                                    "pages": [
                                        {
                                            "page_number": page number goes here,
                                            "summary": "summary of the page goes here",
                                            "tables": [
                                                {
                                                    "table_number": table number goes here,
                                                    "content": [
                                                        ["row1col1", "row1col2", ...],
                                                        ["row2col1", "row2col2", ...],
                                                        ...
                                                    ]
                                                }
                                            ],
                                            "lists": [
                                                {
                                                    "list_number": list number goes here,
                                                    "items": ["item1", "item2", ...]
                                                }
                                            ],
                                            "images": [
                                                {
                                                    "image_number": image number goes here,
                                                    "description": "description of the image goes here"
                                                }
                                            ]
                                        },
                                        ...
                                    ]
                                }
                                - Use clear, descriptive keys for all JSON elements
                                - Preserve formatting where semantically meaningful
                                - Ensure the JSON is valid and well-structured
                                """,
                            },
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {"text": "```json"},
                        ],
                    },
                ],
            }
        ),
        trace="ENABLED",
    )

    return response


def format_ai_response(response_body: dict):
    markdown: str = response_body["output"]["message"]["content"][0]["text"]

    json_response = markdown[:-3].replace('\\"', '"')
    json_response = re.sub(r"(?<!\\)\n", "", json_response).strip()

    return json.loads(json_response)


def get_images(bucket: str, folder: str):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=folder)

    if "Contents" not in response:
        logger.warning(f"No images found in bucket: {bucket}, folder: {folder}")
        return []

    images = []
    for obj in response["Contents"]:
        key = unquote_plus(obj["Key"])
        if key.endswith((".jpg", ".jpeg", ".png")):
            img_content = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            img_ext = os.path.splitext(key)[1][1:]

            images.append(
                {
                    "image": {
                        "format": img_ext,
                        "source": {"bytes": b64encode(img_content).decode("utf-8")},
                    }
                }
            )

    return images
