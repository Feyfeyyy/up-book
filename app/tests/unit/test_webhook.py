from unittest.mock import Mock

import pytest
import requests


class TestWebHookNotifier:
    def test_construct_payload(self, webhook_notifier):
        expected_payload = {
            "app_source": "Up-Book",
            "description": "Up-Book is a simple application to upload books data to S3 and store it in a database.",
            "csv_uploaded": True,
            "csv_filename": "example.csv",
            "s3_url": "https://example.com/s3/path/example.csv",
        }
        assert webhook_notifier._construct_payload() == expected_payload

    def test_make_post_request_success(self, webhook_notifier, monkeypatch):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post = Mock(return_value=mock_response)
        monkeypatch.setattr("requests.post", mock_post)
        assert webhook_notifier._make_post_request({}) == 200

    def test_make_post_request_failure(self, webhook_notifier, monkeypatch):
        mock_post = Mock(side_effect=requests.RequestException)
        monkeypatch.setattr("requests.post", mock_post)
        with pytest.raises(requests.RequestException):
            webhook_notifier._make_post_request({})

    def test_send_notification_success(self, webhook_notifier, monkeypatch):
        mock_make_post_request = Mock(return_value=200)
        monkeypatch.setattr(
            webhook_notifier, "_make_post_request", mock_make_post_request
        )
        assert webhook_notifier.send_notification() == 200

    def test_send_notification_failure(self, webhook_notifier, monkeypatch):
        mock_make_post_request = Mock(side_effect=requests.RequestException)
        monkeypatch.setattr(
            webhook_notifier, "_make_post_request", mock_make_post_request
        )
        with pytest.raises(requests.RequestException):
            webhook_notifier.send_notification()
