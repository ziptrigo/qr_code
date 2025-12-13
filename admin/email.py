#!python
"""
Send emails using AWS SES.

AWS credentials must be configured.
"""


import os
import sys
from typing import Annotated

import typer
from botocore.exceptions import ClientError, NoCredentialsError

from admin.utils import logger

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_SES_SENDER = os.getenv('AWS_SES_SENDER', 'no-reply@joao-coelho.com')


def _send_email(
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
    profile: str | None = None,
):
    import boto3

    if html_body is None:
        html_body = f'<pre>{text_body}</pre>'

    session = boto3.Session(profile_name=profile)
    client = session.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Source=AWS_SES_SENDER,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                },
            },
        )
    except NoCredentialsError:
        logger.error(
            f'AWS credentials not found. Check your AWS profile configuration or '
            f'run: aws configure [--profile {profile or "PROFILE"}]'
        )
        raise typer.Exit(1)
    except ClientError as e:
        logger.error(f'Error sending email: {e}')
        raise typer.Exit(1)

    message_id = response['MessageId']
    logger.info(f'Email sent, MessageId = {message_id}')


@app.command('send')
def email_send(
    to: Annotated[
        str,
        typer.Argument(help='Recipient email address.', show_default=False),
    ],
    subject: Annotated[
        str,
        typer.Option('--subject', '-s', help='Email subject.', show_default=False),
    ],
    text: Annotated[
        str,
        typer.Option('--text', '-t', help='Plain-text body.', show_default=False),
    ],
    html: Annotated[
        str | None,
        typer.Option(
            '--html',
            '-H',
            help='HTML body. If omitted, a simple HTML version of --text is used.',
            show_default=False,
        ),
    ] = None,
    profile: Annotated[
        str | None, typer.Option(help='AWS profile to use.', show_default=False)
    ] = None,
):
    """
    Send a test email via Amazon SES.

    Requires AWS credentials. Use the ``aws`` CLI to configure them.
    """
    try:
        _send_email(
            recipient=to,
            subject=subject,
            text_body=text,
            html_body=html,
            profile=profile,
        )
    except ClientError:
        sys.exit(1)


if __name__ == '__main__':
    app()
