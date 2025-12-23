# Generated manually on 2025-12-08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qr_code', '0004_add_deleted_at_to_qrcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qrcode',
            name='qr_format',
            field=models.CharField(
                choices=[('png', 'PNG'), ('svg', 'SVG'), ('pdf', 'PDF')],
                default='png',
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='qrcode',
            name='error_correction',
            field=models.CharField(
                choices=[
                    ('L', 'Low (~7%)'),
                    ('M', 'Medium (~15%)'),
                    ('Q', 'Quartile (~25%)'),
                    ('H', 'High (~30%)'),
                ],
                default='M',
                max_length=1,
            ),
        ),
    ]
