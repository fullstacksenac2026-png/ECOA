from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0003_remove_user_username_alter_address_cep_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='ddd',
            field=models.CharField(max_length=50),
        ),
    ]
