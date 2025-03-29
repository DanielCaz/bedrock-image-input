import os
import fitz  # type: ignore
import boto3
from urllib.parse import unquote_plus

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

BUCKET_NAME = os.environ["BUCKET_NAME"]

logger = Logger()
tracer = Tracer()

s3 = boto3.client("s3")


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext):
    try:
        bucket = event["bucket"]
        key = unquote_plus(event["key"])

        logger.info(f"Processing PDF from bucket: {bucket}, key: {key}")

        # Get PDF from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        pdf_content = response["Body"].read()

        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        base_key = os.path.splitext(key)[0]

        extracted_images = []

        # Convert each page to an image
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]

            # Convert page to image (uses 300 DPI for good quality)
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))

            # Convert to PNG data
            img_data = pix.tobytes("png")

            # Generate image key
            img_key = f"{base_key}/page_{page_num + 1}.png"

            # Upload to S3
            s3.put_object(
                Bucket=BUCKET_NAME, Key=img_key, Body=img_data, ContentType="image/png"
            )

            extracted_images.append(img_key)
            logger.info(f"Uploaded image: {img_key}")

        pdf_document.close()

        return {
            "message": "Images extracted successfully",
            "output": {"bucket": BUCKET_NAME, "output": base_key},
        }

    except Exception as e:
        logger.exception("Error processing PDF")
        raise e
