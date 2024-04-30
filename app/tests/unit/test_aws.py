import pytest


class TestAWSS3Object:
    def test_connect_to_client_success(self, s3_object):
        assert s3_object._connect_to_client() is not None

    def test_get_client_success(self, s3_object):
        assert s3_object.get_client() is not None

    def test_get_bucket_location_success(self, s3_object):
        mock_client = s3_object.get_client()
        mock_client.meta.client.get_bucket_location.return_value = {
            "LocationConstraint": "us-west-1"
        }
        assert s3_object.get_bucket_location() == "us-west-1"

    def test_upload_s3_file_success(self, s3_object):
        mock_client = s3_object.get_client()
        mock_client.meta.client.upload_file.return_value = None
        assert s3_object.upload_s3_file(path="/path/to/file", key="file.txt") is True

    def test_upload_s3_file_failure(self, s3_object):
        mock_client = s3_object.get_client()
        mock_client.meta.client.upload_file.side_effect = Exception("Upload failed")
        assert s3_object.upload_s3_file(path="/path/to/file", key="file.txt") is False
