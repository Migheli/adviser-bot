# Generated by Django 4.1.7 on 2023-04-02 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contentapp', '0007_remove_article_file_remove_chapter_file_attachment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attachment',
            options={'ordering': ['priority'], 'verbose_name': 'Приложение', 'verbose_name_plural': 'Приложения'},
        ),
        migrations.AddField(
            model_name='attachment',
            name='description',
            field=models.CharField(default='Вложение', max_length=50, verbose_name='Название'),
        ),
    ]
