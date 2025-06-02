from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20231010_1234'),  # Adjust the dependency to the correct previous migration
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='product',
            name='product_title_idx',
        ),
    ]
