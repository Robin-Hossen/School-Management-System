from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teachers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="teacher",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="teachers/",
            ),
        ),
    ]