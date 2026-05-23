import json
import os

import boto3
import subprocess

OUTPUT_BUCKET_NAME = os.environ["OUTPUT_BUCKET_NAME"]

def lambda_handler(event, context):
    try:
        key = event.get("Records")[0].get("s3").get("object").get("key")
        bucket = event.get("Records")[0].get("s3").get("bucket").get("name")

        # Adiciona isso se for rodar localmente
        #
        s3 = boto3.client(
            "s3",
            endpoint_url="http://localhost:4566",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1"
        )

        # s3 = boto3.client(
        #     "s3"
        # )

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


def create_command(input_file, output_file):
    return [
        "ffmpeg",
        "-i", input_file,

        # limita a duração pra 10 segundos
        "-t", "10",

        # Resize (optional)
        "-vf", "scale=512:512:force_original_aspect_ratio=decrease,fps=15",

        # Better animated webp settings
        "-loop", "0",
        "-preset", "default",
        "-an",

        output_file
    ]
