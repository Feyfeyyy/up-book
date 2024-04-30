import json
from typing import Dict

import requests
from loguru import logger
from requests import HTTPError

from app import app

WEBHOOK_REQUEST_URL = app.config["WEBHOOK_REQUEST_URL"]


class WebhookNotifier:
    def __init__(self, csv_filename: str, s3_url: str):
        self.csv_filename = csv_filename
        self.s3_url = s3_url
        self.request_url = WEBHOOK_REQUEST_URL

    def _construct_payload(self) -> Dict:
        return {
            "app_source": "Up-Book",
            "description": "Up-Book is a simple application to upload books data to S3 and store it in a database.",
            "csv_uploaded": True,
            "csv_filename": self.csv_filename,
            "s3_url": self.s3_url,
        }

    def _make_post_request(self, payload: Dict):
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                self.request_url, data=json.dumps(payload), headers=headers
            )
            response.raise_for_status()
            logger.success(f"Successfully Posted To {self.request_url}")
            return response.status_code
        except (requests.RequestException, HTTPError) as e:
            logger.error(f"Error making POST request: {e}")
            raise

    def send_notification(self):
        try:
            payload = self._construct_payload()
            status_code = self._make_post_request(payload)
            return status_code
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise
