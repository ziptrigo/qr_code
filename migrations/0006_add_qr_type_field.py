# Generated manually

from django.db import migrations, models


def set_existing_qrcodes_to_text(apps, schema_editor):
    """Set all existing QR codes to type 'text'."""
    QRCode = apps.get_model('qr_code', 'QRCode')
    QRCode.objects.all().update(qr_type='text')


class Migration(migrations.Migration):

    dependencies = [
        ('qr_code', '0005_convert_to_textchoices'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrcode',
            name='qr_type',
            field=models.CharField(
                blank=True,
                null=True,
                max_length=10,
                choices=[('url', 'URL'), ('text', 'Text')],
                help_text='Type of QR code content',
            ),
        ),
        migrations.RunPython(
            set_existing_qrcodes_to_text,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='qrcode',
            name='qr_type',
            field=models.CharField(
                max_length=10,
                choices=[('url', 'URL'), ('text', 'Text')],
                help_text='Type of QR code content',
            ),
        ),
    ]
