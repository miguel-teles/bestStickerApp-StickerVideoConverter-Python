import json
import os
from datetime import datetime

import boto3
import subprocess
import logging

OUTPUT_BUCKET_NAME = os.environ["OUTPUT_BUCKET_NAME"]
FFMPEG_PATH = "/opt/bin/ffmpeg"

CONFIGS = {
    50: (12, 80),
    100: (12, 75),
    200: (12, 60),
    300: (12, 50),
    500: (10, 60),
    1000: (10, 40),
    2000: (10, 30),
    3000: (10, 20),
}

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

        fps = 12
        input_file = convert_input_into_mp4(fps, input_file, output_key)

        fps, quality = define_webp_convertion_config(input_file)

        logger.info("Trying to convert with fps={},quality={}".format(fps, quality))
        subprocess.run(
            create_command_webp(input_file, output_file, 10, fps, quality),
            check=True
        )

        logger.info("Converted file - size={}".format(os.path.getsize(output_file)))
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


def convert_input_into_mp4(fps, input_file, output_key):
    if input_file.endswith(".gif"):
        logger.info("Converting GIF to MP4 before")
        output_mp4_file = output_key.split('.')[0] + ".mp4"
        subprocess.run(
            create_command_mp4(input_file, output_mp4_file, 10, fps),
            check=True
        )
        input_file = output_mp4_file
    return input_file


def create_command_mp4(input_file,
                       output_file,
                       duration,
                       fps):
    return [
        FFMPEG_PATH,
        "-y",
        "-i", input_file,
        # max duration
        "-t", str(duration),
        # resize + lower fps
        "-vf", f"scale=512:512,fps={fps}",
        "-an",
        "-c:v", "libx264",
        "-crf", "28",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        output_file
    ]


def create_command_webp(input_file,
                        output_file,
                        duration,
                        fps,
                        quality):
    return [
        FFMPEG_PATH,
        "-y",
        "-i", input_file,
        # max duration
        "-t", str(duration),
        # resize + lower fps
        "-vf", f"scale=512:512,fps={fps}",
        # animated webp settings
        "-loop", "0",
        "-an",
        # webp encoder tuning
        "-lossless", "0",
        "-quality", str(quality),
        "-compression_level", "5",
        output_file
    ]

def define_webp_convertion_config(input_file):
    tamanho_arquivo = os.path.getsize(input_file)
    for max_size, (fps, quality) in CONFIGS.items():
        if tamanho_arquivo <= max_size:
            return fps, quality

    return CONFIGS[next(reversed(CONFIGS))]
