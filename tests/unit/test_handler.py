import json

import pytest

from src import app


@pytest.fixture()
def apigw_event():
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
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "test-video.mp4",
                        "size": 34567
                    }
                }
            }
        ]
    }


def test_lambda_handler(apigw_event):

    ret = app.lambda_handler(apigw_event, "")

    assert ret["statusCode"] == 200
    assert "file" in ret["body"]
    assert "bucket" in ret["body"]
