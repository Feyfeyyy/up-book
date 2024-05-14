from unittest.mock import Mock

import pytest
from botocore.exceptions import BotoCoreError

from app.classes.aws import S3Object
from app.classes.webhook import WebhookNotifier


@pytest.fixture
def s3_object():
    # Mock boto3 session and resource
    mock_session = Mock()
    mock_resource = Mock()
    mock_session.resource.return_value = mock_resource
    mock_client = Mock()
    mock_resource.meta.client.return_value = mock_client

    s3_obj = S3Object(
        bucket_name="test_bucket",
        aws_access_key_id="access_key",
        aws_secret_access_key="secret_key",
    )
    s3_obj._connect_to_client = Mock(return_value=mock_client)

    yield s3_obj


@pytest.fixture
def mock_successful_connection(mocker):
    return mocker.patch("boto3.Session.resource")


@pytest.fixture
def mock_failed_connection(mocker):
    return mocker.patch("boto3.Session.resource", side_effect=BotoCoreError)


@pytest.fixture
def webhook_notifier():
    return WebhookNotifier(
        csv_filename="example.csv", s3_url="https://example.com/s3/path/example.csv"
    )
