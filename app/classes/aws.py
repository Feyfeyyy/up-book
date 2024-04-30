import boto3
from loguru import logger


class S3Object:
    def __init__(
        self, bucket_name: str, aws_access_key_id: str, aws_secret_access_key: str
    ):
        self.bucket_name = bucket_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def _connect_to_client(self):
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
            client = session.resource("s3")
            logger.success("Connected to AWS S3 client successfully")
            return client
        except Exception as e:
            logger.error(f"Error connecting to AWS S3 client: {e}")
            raise

    def get_client(self):
        return self._connect_to_client()

    def get_bucket_location(self):
        try:
            client = self.get_client()
            loc = client.meta.client.get_bucket_location(Bucket=self.bucket_name)[
                "LocationConstraint"
            ]
            logger.success(f"Location from bucket {self.bucket_name} is obtained.")
            return loc
        except Exception as e:
            logger.error(
                f"Error retrieving location from bucket {self.bucket_name}: {e}"
            )
            raise

    def upload_s3_file(self, path: str, key: str) -> bool:
        try:
            client = self.get_client()
            client.meta.client.upload_file(path, self.bucket_name, key)
            logger.success(f"Uploaded {path} to {key} in bucket {self.bucket_name}")
            return True
        except Exception as e:
            logger.error(
                f"Error uploading {path} to {key} in bucket {self.bucket_name}: {e}"
            )
            return False
