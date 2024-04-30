from unittest.mock import Mock

import pytest

from app.classes.aws import S3Object


@pytest.fixture
def s3_object():
    # Mock boto3 session and resource
    mock_session = Mock()
    mock_resource = Mock()
    mock_session.resource.return_value = mock_resource
    mock_client = Mock()
    mock_resource.meta.client.return_value = mock_client

    s3_obj = S3Object(bucket_name='test_bucket', aws_access_key_id='access_key', aws_secret_access_key='secret_key')
    s3_obj._connect_to_client = Mock(return_value=mock_client)

    yield s3_obj
