# Generated by Django 2.1.10 on 2019-09-16 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_user_assoc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clients',
            name='reportinterval',
            field=models.IntegerField(blank=True, default=7),
        ),
    ]