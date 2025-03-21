# Generated by Django 3.2.25 on 2025-03-21 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(blank=True, max_length=255, upload_to='attachment/', verbose_name='上传附件'),
        ),
        migrations.AlterField(
            model_name='audio',
            name='audio',
            field=models.FileField(max_length=255, upload_to='audio/', verbose_name='音频'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, max_length=255, upload_to='images/', verbose_name='图片'),
        ),
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(max_length=255, upload_to='video/', verbose_name='视频'),
        ),
    ]
