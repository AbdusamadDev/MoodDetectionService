# Generated by Django 5.0 on 2023-12-13 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_camera_date_recorded_employee_date_recorded_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='./cameras/'),
        ),
        migrations.AlterField(
            model_name='camera',
            name='url',
            field=models.CharField(max_length=150),
        ),
    ]
