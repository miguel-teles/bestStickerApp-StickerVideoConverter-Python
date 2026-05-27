import json
import os
from datetime import datetime

import boto3
import subprocess
import logging

OUTPUT_BUCKET_NAME = os.environ["OUTPUT_BUCKET_NAME"]
FFMPEG_PATH = "/opt/bin/ffmpeg"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    initial_date = datetime.now()
    try:
        key = event.get("Records")[0].get("s3").get("object").get("key")
        bucket = event.get("Records")[0].get("s3").get("bucket").get("name")
        logger.info("Received S3 object key {} from bucket {}".format(key, bucket))

        # Adiciona isso se for rodar localmente
        #
        # s3 = boto3.client(
        #     "s3",
        #     endpoint_url="http://localhost:4566",
        #     aws_access_key_id="test",
        #     aws_secret_access_key="test",
        #     region_name="us-east-1"
        # )

        s3 = boto3.client(
            "s3"
        )

        input_file = "/tmp/" + key
        output_key = "out" + key.split('.')[0] + ".webp"
        output_file = "/tmp/" + output_key

        s3.download_file(bucket, key, input_file)

        command = create_command(input_file, output_file)
        subprocess.run(command, check=True)

        s3.upload_file(output_file, OUTPUT_BUCKET_NAME, output_key)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "file": output_key,
                "bucket": OUTPUT_BUCKET_NAME,
            }),
        }
    except Exception as e:
        print("ERROR:", str(e))
        raise e
    finally:
        final_date = datetime.now()
        execution_duration = (final_date - initial_date).total_seconds()
        logger.info("Processing duration: {}s".format(execution_duration))



def create_command(input_file, output_file):
    return [
        FFMPEG_PATH,
        "-y",
        "-i", input_file,

        # max duration
        "-t", "10",

        # resize + lower fps
        "-vf", "scale=512:512:force_original_aspect_ratio=decrease,fps=12",

        # animated webp settings
        "-loop", "0",
        "-an",

        # webp encoder tuning
        "-lossless", "0",
        "-quality", "30",
        "-compression_level", "0",

        output_file
    ]
