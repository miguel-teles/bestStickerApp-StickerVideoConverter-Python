import json

import pytest
import os

os.environ["OUTPUT_BUCKET_NAME"] = 'test-bucket-out'

from src import app

@pytest.fixture()
def test_mp4():
    """ Generates API GW Event"""

    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "2026-05-15T12:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {
                        "name": "test-bucket-in"
                    },
                    "object": {
                        "key": "video2.mp4",
                        "size": 543879
                    }
                }
            }
        ]
    }

@pytest.fixture()
def test_gif():
    """ Generates API GW Event"""

    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": "2026-05-15T12:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {
                        "name": "test-bucket-in"
                    },
                    "object": {
                        "key": "gif-test.gif",
                        "size": 543879
                    }
                }
            }
        ]
    }


def test_lambda_handler_mp4(test_mp4):
    ret = app.lambda_handler(test_mp4, "")

    assert ret["statusCode"] == 200
    assert "file" in ret["body"]
    assert "bucket" in ret["body"]

    body = json.loads(ret["body"])
    assert body.get("file") == "outvideo2.webp"
    assert body.get("bucket") == "test-bucket-out"

def test_lambda_handler_gif(test_gif):
    ret = app.lambda_handler(test_gif, "")

    assert ret["statusCode"] == 200
    assert "file" in ret["body"]
    assert "bucket" in ret["body"]

    body = json.loads(ret["body"])
    assert body.get("file") == "outgif-test.webp"
    assert body.get("bucket") == "test-bucket-out"
