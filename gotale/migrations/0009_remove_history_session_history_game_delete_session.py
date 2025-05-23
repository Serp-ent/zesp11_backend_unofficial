# Generated by Django 5.1.6 on 2025-04-23 23:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gotale", "0008_alter_game_options_alter_game_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="history",
            name="session",
        ),
        migrations.AddField(
            model_name="history",
            name="game",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="decisions",
                to="gotale.game",
            ),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="Session",
        ),
    ]
