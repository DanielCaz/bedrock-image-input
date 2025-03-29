import os
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

    logger.info(f"Processing images from bucket: {bucket}, folder: {folder}")

    images = get_images(bucket, folder)

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(
            {
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
                                - Return the output as a valid JSON object
                                - Use appropriate nesting to represent document hierarchy
                                - Include a 'pages' array containing content from each page
                                - All extracted text should be summarized and presented in a short, clear and concise manner
                                - Output Schema:
                                [{
                                    "page_number": page number goes here,
                                    "summary": "extracted text goes here",
                                    "tables": [
                                        {
                                            "table_number": table number goes here,
                                            "content": [
                                                ["row1col1", "row1col2"],
                                                ["row2col1", "row2col2"]
                                            ]
                                        }
                                    ],
                                    "lists": [
                                        {
                                            "list_number": list number goes here,
                                            "items": ["item1", "item2"]
                                        }
                                    ],
                                    "images": [
                                        {
                                            "image_number": image number goes here,
                                            "description": "description of the image goes here"
                                        }
                                    ]
                                }]
                                - Use clear, descriptive keys for all JSON elements
                                - Preserve formatting where semantically meaningful
                                - Ensure the JSON is valid and well-structured
                                """,
                            },
                        ],
                    }
                ]
            }
        ),
        trace="ENABLED",
    )

    response_body = json.loads(response["body"].read().decode("utf-8"))

    return {
        "message": "Success",
        "ai_response": response_body,
    }


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
