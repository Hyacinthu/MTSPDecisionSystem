# Generated by Django 3.1.7 on 2021-04-25 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='solution_displayed',
            field=models.CharField(max_length=50, null=True, verbose_name='用来显示的格式化决策结果'),
        ),
    ]