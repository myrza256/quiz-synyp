# Generated by Django 3.1.3 on 2021-01-10 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelectedAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_id', models.IntegerField()),
                ('is_correct', models.BooleanField()),
                ('exam_id', models.IntegerField()),
            ],
        ),
    ]
