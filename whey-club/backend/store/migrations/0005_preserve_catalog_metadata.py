from django.db import migrations

EXTRAS = {1: {'brand_line': 'WHEY CLUB / PURE ISOLATE', 'goals': ['fatloss', 'women']}, 2: {'brand_line': 'WHEY CLUB / DAILY WHEY', 'goals': ['budget']}, 3: {'brand_line': 'WHEY CLUB / PURE ISOLATE', 'goals': ['fatloss', 'women']}, 4: {'brand_line': 'WHEY CLUB / WHEY BLEND', 'goals': ['muscle']}, 5: {'brand_line': 'WHEY CLUB / DAILY WHEY', 'goals': ['budget']}, 6: {'brand_line': 'WHEY CLUB / PURE ISOLATE', 'goals': ['fatloss', 'women']}, 7: {'brand_line': 'WHEY CLUB / CREATINE', 'goals': ['muscle', 'women']}, 8: {'brand_line': 'WHEY CLUB / SHAKER', 'goals': ['muscle', 'fatloss', 'budget', 'women']}}

def copy_existing_metadata(apps,schema_editor):
    Product=apps.get_model('store','Product')
    for pk,values in EXTRAS.items():
        Product.objects.using(schema_editor.connection.alias).filter(pk=pk).update(**values)

class Migration(migrations.Migration):
    dependencies=[('store','0004_product_brand_line_product_goals')]
    operations=[migrations.RunPython(copy_existing_metadata,migrations.RunPython.noop)]
