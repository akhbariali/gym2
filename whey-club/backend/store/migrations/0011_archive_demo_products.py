from django.db import migrations


def archive_demos(apps,schema_editor):
    # Archive preserves admin edits, order references and a reversible recovery path.
    Product=apps.get_model('store','Product')
    Product.objects.filter(is_demo=True,is_active=True).update(is_active=False)


class Migration(migrations.Migration):
    dependencies=[('store','0010_seed_supplier_creatines')]
    operations=[migrations.RunPython(archive_demos,migrations.RunPython.noop)]
