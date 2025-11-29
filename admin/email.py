#!python
"""
Send emails using AWS SES.

AWS credentials must be configured.
"""


import sys
from typing import Annotated

import boto3
import typer
from botocore.exceptions import ClientError

from admin.utils import logger

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


SES_REGION = 'us-east-1'  # change if you created SES in another region
SENDER = 'no-reply@joao-coelho.com'


def _send_email(
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str | None = None,
) -> None:
    if html_body is None:
        html_body = f'<pre>{text_body}</pre>'

    client = boto3.client('ses', region_name=SES_REGION)

    try:
        response = client.send_email(
            Source=SENDER,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                },
            },
        )
    except ClientError as e:
        logger.error(f'Error sending email: {e}')
        raise typer.Exit(1)

    message_id = response['MessageId']
    logger.info(f'Email sent, MessageId = {message_id}')


@app.command('send')
def email_send(
    to: Annotated[
        str,
        typer.Argument(help='Recipient email address.'),
    ],
    subject: Annotated[
        str,
        typer.Option('--subject', '-s', help='Email subject.'),
    ],
    text: Annotated[
        str,
        typer.Option('--text', '-t', help='Plain-text body.'),
    ],
    html: Annotated[
        str | None,
        typer.Option(
            '--html',
            '-H',
            help='HTML body. If omitted, a simple HTML version of --text is used.',
        ),
    ] = None,
) -> None:
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
        )
    except ClientError:
        sys.exit(1)


if __name__ == '__main__':
    app()
