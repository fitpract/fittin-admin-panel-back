# Generated by Django 4.2.13 on 2024-06-14 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_category_child_alter_category_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Storage',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.IntegerField(default=500, verbose_name='total_price'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderedproduct',
            name='price',
            field=models.IntegerField(default=500, verbose_name='ordered_product_price'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default='formed', max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.IntegerField(default=500, verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=40, verbose_name='name'),
        ),
        migrations.CreateModel(
            name='ProductStorage',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('count', models.IntegerField(default=1, verbose_name='amount')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.product')),
                ('storage_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.storage')),
            ],
            options={
                'db_table': 'ProductStorage',
            },
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='media/banner_images/% Y/% m/% d/')),
                ('header', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.product')),
            ],
            options={
                'db_table': 'Banner',
            },
        ),
    ]