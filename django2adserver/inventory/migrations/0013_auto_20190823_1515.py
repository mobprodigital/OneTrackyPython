# Generated by Django 2.1.10 on 2019-08-23 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20190820_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client_access',
            name='clientid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='client_access',
            name='userid',
            field=models.IntegerField(default=0),
        ),
    ]