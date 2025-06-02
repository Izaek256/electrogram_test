from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20231009_1234'),  # Adjust the dependency to the correct previous migration
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['title'], name='product_title_idx'),
        ),
    ]
