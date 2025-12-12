import boto3
from botocore.client import BaseClient


def boto3_client(
    service: str, access_key: str, secret_key: str, role_arn: str, session_name: str = 'S3Session'
) -> BaseClient:
    """
    Create an S3 client by assuming a role.

    :param service: Service name, e.g. ``s3`` or ``ses``.
    :param access_key: IAM user access key ID.
    :param secret_key: IAM user secret access key.
    :param role_arn: ARN of the role to assume.
    :param session_name: Name for the assumed role session.

    :returns: ``boto3`` client with assumed role credentials.
    """
    # Create STS client with user credentials
    sts_client = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    # Assume the role
    response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName=session_name)

    # Extract temporary credentials
    credentials = response['Credentials']

    return boto3.client(  # type: ignore
        service,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
