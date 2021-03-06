# Generated by Django 3.1.3 on 2021-01-11 23:55

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0011_passwordrecovery'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Название категории', max_length=256)),
                ('picture', models.ImageField(blank=True, upload_to='exam_img')),
            ],
            options={
                'verbose_name': 'Тема',
                'verbose_name_plural': 'Темы',
            },
        ),
        migrations.CreateModel(
            name='ThemeQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(default='Текст вопроса', max_length=256)),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.theme')),
            ],
            options={
                'verbose_name': 'Вопрос по теме',
                'verbose_name_plural': 'Вопросы по теме',
            },
        ),
        migrations.AlterModelOptions(
            name='additionalsubjectsrelation',
            options={'verbose_name': 'Зависимость доп. предметов', 'verbose_name_plural': 'Зависимости доп. предметов'},
        ),
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'Ответ ЕНТ', 'verbose_name_plural': 'Ответы ЕНТ'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория ЕНТ', 'verbose_name_plural': 'Категории ЕНТ'},
        ),
        migrations.AlterModelOptions(
            name='exam',
            options={'verbose_name': 'Экзамен ЕНТ', 'verbose_name_plural': 'Экзамены ЕНТ'},
        ),
        migrations.AlterModelOptions(
            name='examsubject',
            options={'verbose_name': 'Предмет ЕНТ', 'verbose_name_plural': 'Предметы ЕНТ'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Вопрос ЕНТ', 'verbose_name_plural': 'Вопросы ЕНТ'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Ученик', 'verbose_name_plural': 'Ученики'},
        ),
        migrations.AlterModelOptions(
            name='variant',
            options={'verbose_name': 'Вариант ЕНТ', 'verbose_name_plural': 'Варианты ЕНТ'},
        ),
        migrations.AlterField(
            model_name='user',
            name='date_created',
            field=models.DateField(default=datetime.date(2021, 1, 12)),
        ),
        migrations.CreateModel(
            name='ThemeRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.theme')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sfsdf', to='exam.theme')),
            ],
            options={
                'verbose_name': 'Зависимость между темами',
                'verbose_name_plural': 'Зависимости между темами',
            },
        ),
        migrations.CreateModel(
            name='ThemeQuestionAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(default='Текст ответа', max_length=256)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.themequestion')),
            ],
            options={
                'verbose_name': 'Ответ на вопрос по теме',
                'verbose_name_plural': 'Ответы на опросы по теме',
            },
        ),
    ]
