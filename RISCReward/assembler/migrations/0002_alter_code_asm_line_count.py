# Generated by Django 4.0.1 on 2022-01-23 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assembler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='code_asm',
            name='line_count',
            field=models.IntegerField(verbose_name='lines'),
        ),
    ]
