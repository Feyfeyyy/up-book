from unittest.mock import Mock

import pytest
from botocore.exceptions import BotoCoreError

from app.classes.aws import S3Object


class TestAWSS3Object:
    def test_connect_to_client_success(self, mock_successful_connection):
        instance = S3Object(
            bucket_name="test_bucket",
            aws_access_key_id="access_key",
            aws_secret_access_key="secret_key",
        )
        assert instance._connect_to_client() is not None
        assert mock_successful_connection.called
        assert instance._connect_to_client() == mock_successful_connection.return_value

    def test_get_client_success(self, mock_successful_connection):
        instance = S3Object(
            bucket_name="test_bucket",
            aws_access_key_id="access_key",
            aws_secret_access_key="secret_key",
        )
        assert instance.get_client() is not None
        assert mock_successful_connection.called
        assert instance.get_client() == mock_successful_connection.return_value

    def test_connect_to_client_failure(self, mock_failed_connection):
        instance = S3Object(
            bucket_name="test_bucket",
            aws_access_key_id="access_key",
            aws_secret_access_key="secret_key",
        )
        with pytest.raises(BotoCoreError):
            instance._connect_to_client()

    def test_get_bucket_location_success(self, s3_object):
        mock_client = s3_object.get_client()
        mock_client.meta.client.get_bucket_location.return_value = {
            "LocationConstraint": "us-west-1"
        }
        assert s3_object.get_bucket_location() == "us-west-1"

    def test_get_bucket_location_failure(self, s3_object):
        # Mocking the behavior of get_client() method
        mock_client = Mock()
        s3_object.get_client = Mock(return_value=mock_client)

        mock_client.meta.client.get_bucket_location.side_effect = Exception(
            "Location retrieval failed"
        )

        with pytest.raises(Exception):
            s3_object.get_bucket_location()

    def test_upload_s3_file_success(self, s3_object):
        mock_client = s3_object.get_client()
        mock_client.meta.client.upload_file.return_value = None
        assert s3_object.upload_s3_file(path="/path/to/file", key="file.txt") is True

    def test_upload_s3_file_failure(self, s3_object):
        mock_client = s3_object.get_client()
        mock_client.meta.client.upload_file.side_effect = Exception("Upload failed")
        assert s3_object.upload_s3_file(path="/path/to/file", key="file.txt") is False
