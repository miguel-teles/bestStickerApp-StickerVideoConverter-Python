#!/bin/bash

set -e

echo "Creating bucket..."

awslocal s3 mb s3://test-bucket-in || true
awslocal s3 mb s3://test-bucket-out || true


echo "Done"
